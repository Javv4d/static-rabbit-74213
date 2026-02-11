#!/usr/bin/env python3
"""
ETL Script for MRR Data Processing
Transforms subscription event data into MRR metrics
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

def load_subscription_events(input_path):
    """Load subscription events from CSV file"""
    events = []
    with open(input_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            events.append({
                'event_id': row['event_id'],
                'customer_id': row['customer_id'],
                'event_type': row['event_type'],
                'event_date': datetime.strptime(row['event_date'], '%Y-%m-%d'),
                'plan_type': row['plan_type'],
                'mrr': float(row['mrr'])
            })
    return events

def calculate_monthly_mrr(events):
    """Calculate MRR for each month"""
    # Group events by customer and date
    customer_state = {}
    monthly_mrr = defaultdict(lambda: {
        'total_mrr': 0,
        'new_mrr': 0,
        'expansion_mrr': 0,
        'contraction_mrr': 0,
        'churn_mrr': 0,
        'active_customers': 0,
        'new_customers': 0,
        'churned_customers': 0
    })
    
    # Sort events by date
    sorted_events = sorted(events, key=lambda x: x['event_date'])
    
    # Find date range
    if not sorted_events:
        return []
    
    start_date = sorted_events[0]['event_date'].replace(day=1)
    end_date = sorted_events[-1]['event_date'].replace(day=1)
    
    # Process events
    for event in sorted_events:
        customer_id = event['customer_id']
        month_key = event['event_date'].strftime('%Y-%m')
        
        if event['event_type'] == 'new_subscription':
            customer_state[customer_id] = event['mrr']
            monthly_mrr[month_key]['new_mrr'] += event['mrr']
            monthly_mrr[month_key]['new_customers'] += 1
        
        elif event['event_type'] == 'upgrade':
            if customer_id in customer_state:
                old_mrr = customer_state[customer_id]
                expansion = event['mrr'] - old_mrr
                monthly_mrr[month_key]['expansion_mrr'] += expansion
                customer_state[customer_id] = event['mrr']
        
        elif event['event_type'] == 'downgrade':
            if customer_id in customer_state:
                old_mrr = customer_state[customer_id]
                contraction = old_mrr - event['mrr']
                monthly_mrr[month_key]['contraction_mrr'] += contraction
                customer_state[customer_id] = event['mrr']
        
        elif event['event_type'] == 'churn':
            if customer_id in customer_state:
                monthly_mrr[month_key]['churn_mrr'] += customer_state[customer_id]
                monthly_mrr[month_key]['churned_customers'] += 1
                del customer_state[customer_id]
    
    # Calculate total MRR and active customers for each month
    current_date = start_date
    results = []
    running_mrr = 0
    
    while current_date <= end_date:
        month_key = current_date.strftime('%Y-%m')
        month_data = monthly_mrr[month_key]
        
        # Calculate net new MRR
        net_new = (month_data['new_mrr'] + 
                   month_data['expansion_mrr'] - 
                   month_data['contraction_mrr'] - 
                   month_data['churn_mrr'])
        
        running_mrr += net_new
        active_customers = len([c for c, mrr in customer_state.items() if mrr > 0])
        
        results.append({
            'month': month_key,
            'total_mrr': round(running_mrr, 2),
            'new_mrr': round(month_data['new_mrr'], 2),
            'expansion_mrr': round(month_data['expansion_mrr'], 2),
            'contraction_mrr': round(month_data['contraction_mrr'], 2),
            'churn_mrr': round(month_data['churn_mrr'], 2),
            'net_new_mrr': round(net_new, 2),
            'active_customers': active_customers,
            'new_customers': month_data['new_customers'],
            'churned_customers': month_data['churned_customers']
        })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return results

def save_mrr_metrics(metrics, output_path):
    """Save MRR metrics to CSV file"""
    fieldnames = [
        'month', 'total_mrr', 'new_mrr', 'expansion_mrr', 
        'contraction_mrr', 'churn_mrr', 'net_new_mrr',
        'active_customers', 'new_customers', 'churned_customers'
    ]
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics)
    
    print(f"Saved {len(metrics)} monthly MRR metrics to {output_path}")

def save_mrr_json(metrics, output_path):
    """Save MRR metrics to JSON file"""
    with open(output_path, 'w') as jsonfile:
        json.dump(metrics, jsonfile, indent=2)
    
    print(f"Saved {len(metrics)} monthly MRR metrics to {output_path}")

def main():
    """Main ETL function"""
    print("Running ETL pipeline...")
    
    # Define paths
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    input_path = data_dir / 'subscription_events.csv'
    
    # Check if input file exists
    if not input_path.exists():
        print(f"Error: Input file {input_path} not found. Please run generate_data.py first.")
        return
    
    # Load and process data
    print(f"Loading subscription events from {input_path}")
    events = load_subscription_events(input_path)
    
    print(f"Calculating monthly MRR metrics...")
    mrr_metrics = calculate_monthly_mrr(events)
    
    # Save results
    csv_output = data_dir / 'mrr_metrics.csv'
    json_output = data_dir / 'mrr_metrics.json'
    
    save_mrr_metrics(mrr_metrics, csv_output)
    save_mrr_json(mrr_metrics, json_output)
    
    # Print summary
    if mrr_metrics:
        print(f"\nETL Pipeline Summary:")
        print(f"Processed {len(events)} events")
        print(f"Generated metrics for {len(mrr_metrics)} months")
        print(f"Latest MRR: ${mrr_metrics[-1]['total_mrr']:,.2f}")
        print(f"Active Customers: {mrr_metrics[-1]['active_customers']}")

if __name__ == '__main__':
    main()
