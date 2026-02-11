# scripts/generate_stripe_test_data.py
#
# Groups customers into clocks of up to 3 customers (Stripe test clock limit).
# For each group:
#   - Pick random start dates in [0..180] days ago for each customer
#   - Create ONE clock at the earliest start date in the group
#   - Create customers on that clock
#   - Advance the clock forward to each customer's start date (if needed) and create their subscription
#   - Then advance forward toward "now" in 31-day steps (or whatever remaining gap is smaller)
#
# Env:
#   STRIPE_SECRET_KEY=sk_test_...
#   NUM_CUSTOMERS=15   (optional)

import os
import random
import time
import datetime as dt

import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

NUM_CUSTOMERS = int(os.environ.get("NUM_CUSTOMERS", "75"))
MAX_DAYS_BACK = 180
STEP_DAYS = 31

random.seed(42)

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
    """Advance clock to target and wait until ready."""
    stripe.test_helpers.TestClock.advance(clock_id, frozen_time=ts(target))
    wait_ready(clock_id)

def create_pm_and_attach(customer_id: str):
    pm = stripe.PaymentMethod.create(type="card", card={"token": "tok_visa"})
    stripe.PaymentMethod.attach(pm.id, customer=customer_id)
    stripe.Customer.modify(customer_id, invoice_settings={"default_payment_method": pm.id})

# ---- shared product + price menu ----
product = stripe.Product.create(name="MRR Demo Product")
PRICE_POINTS = [1900, 2900, 3900, 4900]  # cents
PRICE_IDS = []
for amt in PRICE_POINTS:
    p = stripe.Price.create(
        product=product.id,
        unit_amount=amt,
        currency="usd",
        recurring={"interval": "month"},
    )
    PRICE_IDS.append(p.id)

now = dt.datetime.now(dt.timezone.utc)

# Pre-generate customer configs: random start + random price
customer_cfgs = []
for i in range(NUM_CUSTOMERS):
    days_back = random.randint(0, MAX_DAYS_BACK)
    start_time = now - dt.timedelta(days=days_back)
    price_id = random.choice(PRICE_IDS)
    customer_cfgs.append({"idx": i, "start": start_time, "price": price_id})

# Process in groups of 3
for g_start in range(0, NUM_CUSTOMERS, 3):
    group = customer_cfgs[g_start:g_start + 3]
    group.sort(key=lambda x: x["start"])  # ascending by start date
    group_earliest = group[0]["start"]

    print(f"\n=== Group {g_start//3 + 1}: {len(group)} customer(s) ===")
    print("Start dates:", [x["start"].date().isoformat() for x in group])

    # Create one clock at earliest start
    clock = stripe.test_helpers.TestClock.create(
        frozen_time=ts(group_earliest),
        name=f"group-{g_start//3}-clock",
    )
    clock_id = clock.id
    wait_ready(clock_id)

    # Create customers on this clock + attach PM
    for x in group:
        c = stripe.Customer.create(
            test_clock=clock_id,
            email=f"user{x['idx']}@example.com",
            name=f"User {x['idx']}",
        )
        x["customer_id"] = c.id
        create_pm_and_attach(c.id)

    # Walk forward in time; create each subscription when we reach their start
    current = group_earliest
    for x in group:
        if x["start"] > current:
            # jump directly to next start (difference is always <= STEP_DAYS? not necessarily)
            # user asked: advance by min(31 days, gap). If gap > 31, step 31 until we reach it.
            while current < x["start"]:
                gap_days = (x["start"] - current).days
                step = min(STEP_DAYS, gap_days)
                current = current + dt.timedelta(days=step)
                advance_to(clock_id, current)

        # Now at (or past by a day) their start time — create subscription
        stripe.Subscription.create(
            customer=x["customer_id"],
            items=[{"price": x["price"]}],
        )
        print(f"Subscribed user {x['idx']} on {current.date()} price={x['price']}")

    # Advance from current to now in steps of min(31, remaining gap)
    while current < now:
        gap_days = (now - current).days
        step = min(STEP_DAYS, gap_days)
        current = current + dt.timedelta(days=step)
        advance_to(clock_id, current)

    print(f"Group clock finished at {current.date()} (now={now.date()})")

print("\n✅ DONE")
