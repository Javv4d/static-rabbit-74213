# scripts/query_mrr.py - Query MRR from BigQuery and save results

import os
import json
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

# Config
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS", ""
)
BQ_PROJECT = os.environ["BQ_PROJECT_ID"]

# Read SQL query
with open("sql/mrr_by_month.sql", "r") as f:
    query = f.read()

# Execute query
client = bigquery.Client(project=BQ_PROJECT)
query_job = client.query(query)
results = query_job.result()

# Format results
mrr_data = []
for row in results:
    mrr_data.append({
        "month": row.month,
        "active_subscriptions": int(row.active_subscriptions),
        "avg_monthly_amount_usd": float(row.avg_monthly_amount_usd),
        "mrr_amount": float(row.mrr_amount)
    })

# Print results
print("MRR by Month:")
print("-" * 40)
for item in mrr_data:
    print(f"{item['month']}: ${item['mrr_amount']:,.2f}")

# Save to frontend mock data
output_path = "frontend/src/data/mockMrr.json"
with open(output_path, "w") as f:
    json.dump(mrr_data, f, indent=2)

print(f"\n✅ Saved {len(mrr_data)} months to {output_path}")
