import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Load the simulated data
try:
    suppliers = pd.read_csv('data/suppliers.csv')
    shipments = pd.read_csv('data/shipments.csv')
    events = pd.read_csv('data/events.csv')
except FileNotFoundError:
    st.error("Data files not found. Please run 'python src/simulate_data.py' first.")
    st.stop()

# --- Data Preprocessing and Feature Engineering ---
# Convert date columns to datetime objects
shipments['shipment_date'] = pd.to_datetime(shipments['shipment_date'])
shipments['actual_delivery_date'] = pd.to_datetime(shipments['actual_delivery_date'])
shipments['scheduled_delivery_date'] = pd.to_datetime(shipments['scheduled_delivery_date'])

# Calculate shipment delays
shipments['delay_days'] = (shipments['actual_delivery_date'] - shipments['scheduled_delivery_date']).dt.days

# Join dataframes
full_df = pd.merge(shipments, suppliers, on='supplier_id', how='left')

# --- Streamlit Dashboard ---
st.set_page_config(layout="wide", page_title="Supply Chain Risk Dashboard")

st.title("Supply Chain Risk Analysis")

st.markdown("""
This dashboard provides a high-level overview of supply chain risks.
Analyze key metrics, identify vulnerable suppliers, and understand potential impacts.
""")

# --- KPI Section ---
total_suppliers = suppliers.shape[0]
avg_on_time_rate = suppliers['historical_on_time_rate'].mean() * 100
total_shipments = shipments.shape[0]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Suppliers", value=total_suppliers)
with col2:
    st.metric(label="Avg. On-Time Rate", value=f"{avg_on_time_rate:.1f}%")
with col3:
    st.metric(label="Total Shipments", value=total_shipments)

st.write("---")

# --- Supplier Performance Chart ---
st.header("Supplier Performance")
st.markdown("Identify the top and worst performing suppliers based on on-time delivery rate.")

# Sort suppliers by on-time rate
top_suppliers = suppliers.sort_values('historical_on_time_rate', ascending=False).head(10)
worst_suppliers = suppliers.sort_values('historical_on_time_rate').head(10)

fig_suppliers = go.Figure()
fig_suppliers.add_trace(go.Bar(
    x=top_suppliers['supplier_id'],
    y=top_suppliers['historical_on_time_rate'],
    name='Top 10 On-Time Rate',
    marker_color='green'
))
fig_suppliers.add_trace(go.Bar(
    x=worst_suppliers['supplier_id'],
    y=worst_suppliers['historical_on_time_rate'],
    name='Worst 10 On-Time Rate',
    marker_color='red'
))
st.plotly_chart(fig_suppliers, use_container_width=True)

st.write("---")

# --- Risk & Events Section ---
st.header("Risk & Event Analysis")
st.markdown("Explore historical risk events and their potential impact.")

fig_events = px.bar(events, x='event_type', title='Distribution of Historical Risk Events')
st.plotly_chart(fig_events, use_container_width=True)

# Map of supplier and event locations (requires geocoding, so we'll simulate a simple map)
st.subheader("Geographic Risk Map (Simulated)")
st.write("This map would show supplier locations and highlight regions with historical risk events.")
# We will use a simple scatter map as a placeholder since we don't have real lat/long data
df_map = pd.DataFrame({
    'lat': np.random.uniform(20, 50, size=total_suppliers),
    'lon': np.random.uniform(-100, -60, size=total_suppliers),
    'size': suppliers['financial_health_score'] * 10
})
fig_map = px.scatter_mapbox(df_map, lat='lat', lon='lon', size='size', zoom=2,
                            title='Simulated Supplier Locations by Financial Health')
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map)

# --- Scenario Analysis (Conceptual) ---
st.write("---")
st.header("Scenario Planning: What If?")
st.markdown("Conceptual tool to simulate a disruption and see the impact on shipment delays.")
supplier_to_test = st.selectbox("Select a Supplier to simulate a delay:", suppliers['supplier_id'].unique())
delay_days = st.slider("Simulated Delay (Days)", 0, 30, 5)

if st.button("Run Simulation"):
    avg_delay_for_supplier = full_df[full_df['supplier_id'] == supplier_to_test]['delay_days'].mean()
    new_avg_delay = avg_delay_for_supplier + delay_days
    st.success(f"Simulating a {delay_days}-day delay for {supplier_to_test}.")
    st.info(f"The average delay for this supplier would increase from {avg_delay_for_supplier:.2f} days to {new_avg_delay:.2f} days.")
    st.info("Additional analysis would show impacts on downstream inventory and costs.")