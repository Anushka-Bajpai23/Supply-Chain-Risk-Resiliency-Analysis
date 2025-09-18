import pandas as pd
import numpy as np
from faker import Faker

# Initialize Faker for realistic-looking data
fake = Faker()

def generate_supply_chain_data(num_suppliers=50, num_shipments=500, num_events=30):
    """Generates a synthetic supply chain dataset."""
    
    # 1. Supplier Data
    suppliers = []
    for i in range(num_suppliers):
        suppliers.append({
            'supplier_id': f'SUP{i:03d}',
            'supplier_location': fake.city() + ', ' + fake.country(),
            'financial_health_score': np.random.randint(1, 10),
            'historical_on_time_rate': np.random.uniform(0.6, 1.0)
        })
    suppliers_df = pd.DataFrame(suppliers)
    
    # 2. Shipment Data
    shipments = []
    for i in range(num_shipments):
        supplier_id = np.random.choice(suppliers_df['supplier_id'])
        is_delayed = np.random.choice([0, 1], p=[0.85, 0.15]) # 15% chance of delay
        shipments.append({
            'shipment_id': f'SHIP{i:04d}',
            'supplier_id': supplier_id,
            'shipment_date': fake.date_this_year(),
            'scheduled_delivery_date': fake.date_this_year(),
            'actual_delivery_date': fake.date_this_year() + pd.to_timedelta(np.random.randint(0, 30) * is_delayed, unit='D'),
            'transport_mode': np.random.choice(['Air', 'Sea', 'Rail', 'Truck']),
            'product_sku': fake.ean13()
        })
    shipments_df = pd.DataFrame(shipments)
    
    # 3. Event Data
    events = []
    event_types = ['Natural Disaster', 'Geopolitical Conflict', 'Port Closure', 'Labor Strike', 'Supplier Bankruptcy']
    for i in range(num_events):
        events.append({
            'event_id': f'EVT{i:03d}',
            'event_type': np.random.choice(event_types),
            'event_location': fake.city() + ', ' + fake.country(),
            'event_start_date': fake.date_this_year(),
            'event_end_date': fake.date_this_year() + pd.to_timedelta(np.random.randint(2, 20), unit='D')
        })
    events_df = pd.DataFrame(events)

    # Save to CSV
    suppliers_df.to_csv('data/suppliers.csv', index=False)
    shipments_df.to_csv('data/shipments.csv', index=False)
    events_df.to_csv('data/events.csv', index=False)
    print("Data simulation complete. Files saved to the 'data' folder.")

if __name__ == '__main__':
    generate_supply_chain_data()