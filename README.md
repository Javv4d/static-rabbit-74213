# MRR Analytics Dashboard

A complete Monthly Recurring Revenue (MRR) analytics application with data generation, ETL pipeline, SQL analytics, and a React dashboard.

## 📦 Project Structure

```
.
├── README.md                 # This file
├── scripts/                  # Python scripts for data generation and ETL
│   ├── generate_data.py     # Generates sample subscription data
│   └── etl_pipeline.py      # Processes data and calculates MRR metrics
├── sql/                      # SQL queries for MRR analysis
│   ├── calculate_mrr.sql    # BigQuery MRR calculation logic
│   └── query_mrr.sql        # SQLite query for local development
├── frontend/                 # React dashboard application
│   ├── src/
│   │   ├── App.jsx          # Main application component
│   │   ├── components/
│   │   │   └── Dashboard.jsx # Dashboard with charts
│   └── package.json
└── data/                     # Generated data (not committed to git)
    ├── subscription_events.csv
    ├── subscription_events.json
    ├── mrr_metrics.csv
    └── mrr_metrics.json
```

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Node.js 18 or higher
- npm or yarn

### Step 1: Generate Sample Data

First, generate sample subscription data:

```bash
python scripts/generate_data.py
```

This will create:
- `data/subscription_events.csv` - Raw subscription events
- `data/subscription_events.json` - Same data in JSON format

The script generates realistic subscription data including:
- New subscriptions
- Plan upgrades
- Customer churn events
- Multiple plan types (Basic: $29.99, Pro: $99.99, Enterprise: $299.99)

### Step 2: Run ETL Pipeline

Process the raw data to calculate MRR metrics:

```bash
python scripts/etl_pipeline.py
```

This will create:
- `data/mrr_metrics.csv` - Calculated MRR metrics by month
- `data/mrr_metrics.json` - Same metrics in JSON format

The ETL pipeline calculates:
- Total MRR
- New MRR (from new subscriptions)
- Expansion MRR (from upgrades)
- Contraction MRR (from downgrades)
- Churn MRR (from cancellations)
- Net New MRR
- Active customer counts
- Customer acquisition and churn numbers

### Step 3: Start the Dashboard

Install frontend dependencies:

```bash
cd frontend
npm install
```

Start the development server:

```bash
npm run dev
```

The dashboard will open automatically at `http://localhost:3000`

## 📊 Dashboard Features

The MRR Analytics Dashboard includes:

### Key Metrics Cards
- **Total MRR** - Current monthly recurring revenue with trend indicator
- **Active Customers** - Number of active subscriptions with growth percentage
- **New MRR** - Revenue from new customers this month
- **Churn MRR** - Revenue lost from cancellations this month

### Interactive Charts
1. **MRR Trend** - Area chart showing total MRR growth over time
2. **Active Customers** - Line chart tracking customer base growth
3. **MRR Breakdown** - Stacked bar chart showing new, expansion, contraction, and churn MRR
4. **Customer Growth** - Bar chart comparing new vs churned customers

## 🗄️ SQL Queries

### BigQuery
The `sql/calculate_mrr.sql` file contains production-ready BigQuery SQL for calculating MRR metrics from a subscription events table. It includes:
- Event timeline processing
- Customer state tracking
- Monthly aggregations
- Growth rate calculations

### Local Development
The `sql/query_mrr.sql` provides a simplified SQLite-compatible query for local testing and development.

## 🧪 Data Schema

### Subscription Events
```
event_id        - Unique event identifier
customer_id     - Unique customer identifier
event_type      - Type of event (new_subscription, upgrade, downgrade, churn)
event_date      - Date of the event (YYYY-MM-DD)
plan_type       - Subscription plan (basic, pro, enterprise)
mrr             - Monthly recurring revenue amount
```

### MRR Metrics
```
month              - Month (YYYY-MM)
total_mrr          - Total MRR at end of month
new_mrr            - MRR from new customers
expansion_mrr      - MRR increase from upgrades
contraction_mrr    - MRR decrease from downgrades
churn_mrr          - MRR lost from cancellations
net_new_mrr        - Net change in MRR
active_customers   - Number of active customers
new_customers      - New customers acquired
churned_customers  - Customers who cancelled
```

## 🛠️ Development

### Build Frontend for Production

```bash
cd frontend
npm run build
```

The production build will be created in `frontend/dist/`

### Preview Production Build

```bash
cd frontend
npm run preview
```

## 📝 Notes

- Sample data covers the period from January 2024 to February 2026
- The data generator creates approximately 500 customers with realistic churn and upgrade patterns
- All monetary values are in USD
- The dashboard automatically refreshes when data files are updated

## 🔧 Customization

### Modify Data Generation Parameters

Edit `scripts/generate_data.py` to adjust:
- `NUM_CUSTOMERS` - Number of initial customers
- `START_DATE` / `END_DATE` - Date range for data generation
- `PLAN_TYPES` - Subscription plans and pricing

### Customize Dashboard

The dashboard can be customized by editing:
- `frontend/src/components/Dashboard.jsx` - Chart types and metrics
- `frontend/src/components/Dashboard.css` - Styling and colors

## 📄 License

MIT License - feel free to use this project for learning or commercial purposes.