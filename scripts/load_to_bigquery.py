"""Extract Stripe data and load to BigQuery.

Requires:
- STRIPE_API_KEY
- GCP_PROJECT
- BQ_DATASET
- BQ_TABLE (default: stripe_invoices)
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
import stripe
from google.cloud import bigquery

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
GCP_PROJECT = os.getenv("GCP_PROJECT")
BQ_DATASET = os.getenv("BQ_DATASET")
BQ_TABLE = os.getenv("BQ_TABLE", "stripe_invoices")

if not STRIPE_API_KEY:
    raise SystemExit("Missing STRIPE_API_KEY in environment.")
if not GCP_PROJECT or not BQ_DATASET:
    raise SystemExit("Missing GCP_PROJECT or BQ_DATASET in environment.")

stripe.api_key = STRIPE_API_KEY


def fetch_invoices(limit: int = 1000):
    invoices = []
    for invoice in stripe.Invoice.list(limit=limit).auto_paging_iter():
        invoices.append(
            {
                "invoice_id": invoice.id,
                "customer_id": invoice.customer,
                "subscription_id": invoice.subscription,
                "status": invoice.status,
                "amount_paid": invoice.amount_paid,
                "currency": invoice.currency,
                "created": datetime.fromtimestamp(invoice.created, tz=timezone.utc).isoformat(),
                "period_start": datetime.fromtimestamp(invoice.period_start, tz=timezone.utc).isoformat()
                if invoice.period_start
                else None,
                "period_end": datetime.fromtimestamp(invoice.period_end, tz=timezone.utc).isoformat()
                if invoice.period_end
                else None,
            }
        )
    return invoices


def load_to_bigquery(rows):
    client = bigquery.Client(project=GCP_PROJECT)
    table_id = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("invoice_id", "STRING"),
            bigquery.SchemaField("customer_id", "STRING"),
            bigquery.SchemaField("subscription_id", "STRING"),
            bigquery.SchemaField("status", "STRING"),
            bigquery.SchemaField("amount_paid", "INT64"),
            bigquery.SchemaField("currency", "STRING"),
            bigquery.SchemaField("created", "TIMESTAMP"),
            bigquery.SchemaField("period_start", "TIMESTAMP"),
            bigquery.SchemaField("period_end", "TIMESTAMP"),
        ],
        write_disposition="WRITE_TRUNCATE",
    )

    load_job = client.load_table_from_json(rows, table_id, job_config=job_config)
    load_job.result()
    print(f"Loaded {len(rows)} rows into {table_id}.")


if __name__ == "__main__":
    data = fetch_invoices()
    load_to_bigquery(data)
