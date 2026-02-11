# static-rabbit-74213

MRR dashboard demo using Stripe, BigQuery, and React.

## Structure
- scripts/: Stripe data generator + BigQuery loader
- sql/: MRR query
- frontend/: React dashboard

## Prerequisites
- Stripe test account + API key
- Google Cloud project + BigQuery dataset
- Python 3.10+
- Node 18+

## Setup
1) Install Python deps:
	- pip install -r scripts/requirements.txt
2) Set env vars (example):
	- STRIPE_API_KEY=sk_test_...
	- GCP_PROJECT=your-gcp-project
	- BQ_DATASET=your_dataset

## Generate Stripe test data
- python scripts/generate_stripe_test_data.py

## Load Stripe data to BigQuery
- python scripts/load_to_bigquery.py

## Run MRR query
- Open [sql/mrr_by_month.sql](sql/mrr_by_month.sql) in BigQuery
- Replace project.dataset with your values

## Run frontend
1) cd frontend
2) npm install
3) npm run dev

Note: The UI currently loads mock data in [frontend/src/api.js](frontend/src/api.js). Flip `USE_MOCK` to false once you expose an API endpoint for BigQuery.