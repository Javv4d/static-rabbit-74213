# scripts/generate_stripe_test_data.py
#
# - Groups customers into clocks of up to 3 (Stripe limit).
# - Each customer has a random start date in [0..MAX_DAYS_BACK] days ago.
# - Each customer picks a random price from a pre-made menu.
# - On subscription creation:
#     - OVERDUE_PROB chance: clear default payment method (""), so future invoices go past_due.
# - Before EACH time advance step:
#     - CANCEL_PROB chance: cancel any active subscription (created and not already canceled).
#   This happens even while other customers in the same clock group haven’t started yet.
#
# Env:
#   STRIPE_SECRET_KEY=sk_test_...
#   NUM_CUSTOMERS=15
#   MAX_DAYS_BACK=180
#   STEP_DAYS=31
#   OVERDUE_PROB=0.10
#   CANCEL_PROB=0.05
#   SEED=42

import os
import random
import time
import datetime as dt

import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

NUM_CUSTOMERS = int(os.environ.get("NUM_CUSTOMERS", "75"))
MAX_DAYS_BACK = int(os.environ.get("MAX_DAYS_BACK", "180"))
STEP_DAYS = int(os.environ.get("STEP_DAYS", "31"))
OVERDUE_PROB = float(os.environ.get("OVERDUE_PROB", "0.10"))
CANCEL_PROB = float(os.environ.get("CANCEL_PROB", "0.20"))
random.seed(int(os.environ.get("SEED", "43")))

def ts(d: dt.datetime) -> int:
    return int(d.timestamp())

def wait_ready(clock_id: str, timeout_s: int = 180):
    t0 = time.time()
    while True:
        c = stripe.test_helpers.TestClock.retrieve(clock_id)
        if c.status == "ready":
            return
        if time.time() - t0 > timeout_s:
            raise TimeoutError(f"Clock {clock_id} not ready after {timeout_s}s (status={c.status})")
        time.sleep(1)

def advance_to(clock_id: str, target: dt.datetime):
    stripe.test_helpers.TestClock.advance(clock_id, frozen_time=ts(target))
    wait_ready(clock_id)

def attach_visa(customer_id: str):
    pm = stripe.PaymentMethod.create(type="card", card={"token": "tok_visa"})
    stripe.PaymentMethod.attach(pm.id, customer=customer_id)
    stripe.Customer.modify(customer_id, invoice_settings={"default_payment_method": pm.id})

# ---- Shared product + price menu ----
product = stripe.Product.create(name="MRR Demo Product")
PRICE_POINTS = [1900, 2900, 3900, 4900]
PRICE_IDS = [
    stripe.Price.create(
        product=product.id,
        unit_amount=amt,
        currency="usd",
        recurring={"interval": "month"},
    ).id
    for amt in PRICE_POINTS
]

now = dt.datetime.now(dt.timezone.utc)

# Pre-generate customers
cfgs = []
for i in range(NUM_CUSTOMERS):
    start = now - dt.timedelta(days=random.randint(0, MAX_DAYS_BACK))
    cfgs.append({
        "idx": i,
        "start": start,
        "price": random.choice(PRICE_IDS),
        "customer_id": None,
        "sub_id": None,
        "canceled": False,
        "overdue": False,
        "sub_created": False,
    })

# Process in groups of up to 3 per clock
for g_start in range(0, NUM_CUSTOMERS, 3):
    group = cfgs[g_start:g_start + 3]
    group.sort(key=lambda x: x["start"])  # chronological starts
    earliest = group[0]["start"]

    print(f"\n=== Group {g_start//3 + 1}: {len(group)} customer(s) ===")
    print("starts:", [x["start"].date().isoformat() for x in group])

    # One clock per group, starting at earliest start
    clock = stripe.test_helpers.TestClock.create(
        frozen_time=ts(earliest),
        name=f"group-{g_start//3}-clock",
    )
    clock_id = clock.id
    wait_ready(clock_id)

    # Create customers on the clock and attach a card (required to create auto-charge subs)
    for x in group:
        cust = stripe.Customer.create(
            test_clock=clock_id,
            email=f"user{x['idx']}@example.com",
            name=f"User {x['idx']}",
        )
        x["customer_id"] = cust.id
        attach_visa(cust.id)

    current = earliest

    # Drive time forward until now, creating subs at their starts and canceling along the way
    while current < now:
        # 1) Create any subscriptions whose start time has been reached
        for x in group:
            if (not x["sub_created"]) and (x["start"] <= current):
                sub = stripe.Subscription.create(
                    customer=x["customer_id"],
                    items=[{"price": x["price"]}],
                    collection_method="charge_automatically",
                )
                x["sub_id"] = sub.id
                x["sub_created"] = True

                # Overdue cohort: clear default PM right after creation ("" clears correctly)
                if random.random() < OVERDUE_PROB:
                    stripe.Customer.modify(
                        x["customer_id"],
                        invoice_settings={"default_payment_method": ""},
                    )
                    x["overdue"] = True

                print(
                    f"created sub user={x['idx']} start={x['start'].date()} "
                    f"price={x['price']} overdue={x['overdue']}"
                )

        # 2) Before the next advance, give every active sub a chance to cancel
        for x in group:
            if x["sub_created"] and (not x["canceled"]) and (not x["overdue"]):
                if random.random() < CANCEL_PROB:
                    stripe.Subscription.cancel(x["sub_id"])
                    x["canceled"] = True
                    print(f"canceled user={x['idx']} sub={x['sub_id']} at {current.date()}")

        # 3) Choose next time to jump to:
        #    - next customer start (so we can create their sub exactly at/after start)
        #    - or current + STEP_DAYS
        #    - or now
        next_starts = [x["start"] for x in group if not x["sub_created"] and x["start"] > current]
        next_start = min(next_starts) if next_starts else None

        step_target = current + dt.timedelta(days=STEP_DAYS)
        candidates = [now, step_target]
        if next_start is not None:
            candidates.append(next_start)

        target = min(candidates)

        # If target == current, avoid infinite loop (can happen with same-day starts)
        if target <= current:
            target = min(now, current + dt.timedelta(days=1))

        current = target
        advance_to(clock_id, current)

    print(f"group finished at {current.date()}")

print("\n✅ DONE")
