# scripts/load_to_bq.py - Stripe to BigQuery ETL Pipeline (MRR-focused)

import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import stripe
from google.cloud import bigquery

load_dotenv()

# Config
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS", ""
)
BQ_PROJECT = os.environ["BQ_PROJECT_ID"]
BQ_DATASET = os.environ["BQ_DATASET"]


def fetch_stripe_mrr_data():
    """Fetch MRR-relevant data: subscriptions."""
    print("Fetching Stripe MRR data...")
    
    # Get all customers (from test clocks and regular)
    customers = []
    try:
        all_clocks = list(stripe.test_helpers.TestClock.list(limit=100))
        print(f"Found {len(all_clocks)} test clocks")
        for clock in all_clocks:
            clock_customers = stripe.Customer.list(test_clock=clock.id, limit=1000)
            for cust in clock_customers.auto_paging_iter():
                customers.append(cust.id)
    except Exception as e:
        print(f"Error fetching test clock customers: {e}")
    
    # Regular customers
    cust_list = stripe.Customer.list(limit=1000)
    for cust in cust_list.auto_paging_iter():
        if cust.id not in customers:
            customers.append(cust.id)
    print(f"Found {len(customers)} customers")
    
    # Fetch subscriptions with recurring amounts
    subscriptions = []
    print("Fetching subscriptions...")
    for cust_id in customers:
        try:
            subs = stripe.Subscription.list(customer=cust_id, limit=100, status="all")
            for sub in subs.auto_paging_iter():
                # Calculate monthly recurring amount from items
                monthly_amount = 0
                for item in sub.get("items", {}).get("data", []):
                    if item.price and item.price.recurring:
                        amount = item.price.unit_amount * item.quantity
                        interval = item.price.recurring.get("interval")
                        # Normalize to monthly
                        if interval == "month":
                            monthly_amount += amount
                        elif interval == "year":
                            monthly_amount += amount / 12
                
                subscriptions.append({
                    "subscription_id": sub.id,
                    "customer_id": sub.customer,
                    "status": sub.status,
                    "monthly_amount": int(monthly_amount),  # In cents
                    "created": datetime.fromtimestamp(sub.created, tz=timezone.utc).isoformat(),
                    "canceled_at": datetime.fromtimestamp(sub.canceled_at, tz=timezone.utc).isoformat() if sub.canceled_at else None,
                    "current_period_start": datetime.fromtimestamp(sub.current_period_start, tz=timezone.utc).isoformat(),
                    "current_period_end": datetime.fromtimestamp(sub.current_period_end, tz=timezone.utc).isoformat(),
                })
        except Exception as e:
            print(f"  Error fetching subscriptions for {cust_id}: {e}")
    print(f"Fetched {len(subscriptions)} subscriptions")
    
    return subscriptions


def load_to_bigquery(subscriptions):
    """Load MRR data into BigQuery tables."""
    print("\nLoading data to BigQuery...")
    
    client = bigquery.Client(project=BQ_PROJECT)
    
    # Create dataset if it doesn't exist
    dataset_id = f"{BQ_PROJECT}.{BQ_DATASET}"
    try:
        client.get_dataset(dataset_id)
        print(f"Dataset {dataset_id} already exists")
    except:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"Created dataset {dataset_id}")
    
    # Load subscriptions
    subscriptions_table = f"{dataset_id}.subscriptions"
    subscriptions_schema = [
        bigquery.SchemaField("subscription_id", "STRING"),
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("monthly_amount", "INT64"),
        bigquery.SchemaField("created", "TIMESTAMP"),
        bigquery.SchemaField("canceled_at", "TIMESTAMP"),
        bigquery.SchemaField("current_period_start", "TIMESTAMP"),
        bigquery.SchemaField("current_period_end", "TIMESTAMP"),
    ]
    load_table(client, subscriptions, subscriptions_table, subscriptions_schema)
    
    print("\n✅ ETL Complete!")
    print(f"Subscriptions table: {subscriptions_table}")


def load_table(client, data, table_id, schema):
    """Helper to load data into a BigQuery table."""
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition="WRITE_TRUNCATE",  # Replace existing data
    )
    
    job = client.load_table_from_json(data, table_id, job_config=job_config)
    job.result()  # Wait for completion
    
    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows into {table_id}")


if __name__ == "__main__":
    subscriptions = fetch_stripe_mrr_data()
    load_to_bigquery(subscriptions)
