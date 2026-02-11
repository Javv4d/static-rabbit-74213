#!/usr/bin/env python3
"""
Data Generator for Subscription-based SaaS Application
Generates sample subscription data for MRR analysis
"""

import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
NUM_CUSTOMERS = 500
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 2, 1)
PLAN_TYPES = {
    'basic': 29.99,
    'pro': 99.99,
    'enterprise': 299.99
}

def generate_customer_id():
    """Generate a unique customer ID"""
    return f"CUST-{random.randint(10000, 99999)}"

def generate_subscription_events():
    """Generate subscription events (new, upgrade, downgrade, churn)"""
    events = []
    customer_ids = set()
    
    # Generate initial subscriptions
    current_date = START_DATE
    while current_date <= END_DATE:
        # New subscriptions
        if random.random() < 0.3:  # 30% chance of new subscription per day
            num_new = random.randint(1, 5)
            for _ in range(num_new):
                customer_id = generate_customer_id()
                while customer_id in customer_ids:
                    customer_id = generate_customer_id()
                customer_ids.add(customer_id)
                
                plan = random.choice(list(PLAN_TYPES.keys()))
                events.append({
                    'event_id': f"EVT-{len(events)+1:06d}",
                    'customer_id': customer_id,
                    'event_type': 'new_subscription',
                    'event_date': current_date.strftime('%Y-%m-%d'),
                    'plan_type': plan,
                    'mrr': PLAN_TYPES[plan]
                })
        
        current_date += timedelta(days=1)
    
    # Generate upgrades, downgrades, and churns for existing customers
    active_customers = {}
    for event in events:
        if event['event_type'] == 'new_subscription':
            active_customers[event['customer_id']] = {
                'plan': event['plan_type'],
                'start_date': datetime.strptime(event['event_date'], '%Y-%m-%d')
            }
    
    # Add some lifecycle events
    additional_events = []
    for customer_id, customer_data in list(active_customers.items()):
        # Random chance of upgrade/downgrade/churn
        days_since_start = (END_DATE - customer_data['start_date']).days
        
        if days_since_start > 30:
            event_date = customer_data['start_date'] + timedelta(days=random.randint(30, min(days_since_start, 365)))
            
            # 10% chance of upgrade
            if customer_data['plan'] != 'enterprise' and random.random() < 0.1:
                new_plan = 'pro' if customer_data['plan'] == 'basic' else 'enterprise'
                additional_events.append({
                    'event_id': f"EVT-{len(events)+len(additional_events)+1:06d}",
                    'customer_id': customer_id,
                    'event_type': 'upgrade',
                    'event_date': event_date.strftime('%Y-%m-%d'),
                    'plan_type': new_plan,
                    'mrr': PLAN_TYPES[new_plan]
                })
                customer_data['plan'] = new_plan
            
            # 15% chance of churn
            elif random.random() < 0.15 and days_since_start > 60:
                churn_date = customer_data['start_date'] + timedelta(days=random.randint(60, days_since_start))
                additional_events.append({
                    'event_id': f"EVT-{len(events)+len(additional_events)+1:06d}",
                    'customer_id': customer_id,
                    'event_type': 'churn',
                    'event_date': churn_date.strftime('%Y-%m-%d'),
                    'plan_type': customer_data['plan'],
                    'mrr': 0
                })
    
    events.extend(additional_events)
    events.sort(key=lambda x: x['event_date'])
    
    return events

def save_to_csv(events, output_path):
    """Save events to CSV file"""
    fieldnames = ['event_id', 'customer_id', 'event_type', 'event_date', 'plan_type', 'mrr']
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)
    
    print(f"Generated {len(events)} events and saved to {output_path}")

def save_to_json(events, output_path):
    """Save events to JSON file"""
    with open(output_path, 'w') as jsonfile:
        json.dump(events, jsonfile, indent=2)
    
    print(f"Generated {len(events)} events and saved to {output_path}")

def main():
    """Main function to generate data"""
    print("Generating subscription data...")
    events = generate_subscription_events()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # Save to both CSV and JSON
    csv_path = output_dir / 'subscription_events.csv'
    json_path = output_dir / 'subscription_events.json'
    
    save_to_csv(events, csv_path)
    save_to_json(events, json_path)
    
    # Print statistics
    print(f"\nData Generation Statistics:")
    print(f"Total events: {len(events)}")
    print(f"New subscriptions: {sum(1 for e in events if e['event_type'] == 'new_subscription')}")
    print(f"Upgrades: {sum(1 for e in events if e['event_type'] == 'upgrade')}")
    print(f"Churns: {sum(1 for e in events if e['event_type'] == 'churn')}")

if __name__ == '__main__':
    main()
