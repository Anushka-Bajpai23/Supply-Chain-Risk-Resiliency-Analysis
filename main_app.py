import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from faker import Faker
import os

# --- 1. User Authentication (Same as before) ---
users = {"user1": "pass123", "admin": "admin"}

def login_page():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in users and users[username] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password")

def signup_page():
    st.sidebar.title("Sign Up")
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type="password")
    if st.sidebar.button("Create Account"):
        if new_username in users:
            st.sidebar.error("Username already exists!")
        else:
            users[new_username] = new_password
            st.sidebar.success("Account created! Please log in.")
            
def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.rerun()

# --- 2. Dynamic Data Simulation based on User Input ---
def generate_dynamic_data(num_suppliers, num_shipments):
    """Generates a synthetic supply chain dataset based on user input."""
    fake = Faker()
    
    # Supplier Data
    suppliers = []
    for i in range(num_suppliers):
        suppliers.append({
            'supplier_id': f'SUP{i:03d}',
            'supplier_location': fake.city() + ', ' + fake.country(),
            'financial_health_score': np.random.randint(1, 10),
            'historical_on_time_rate': np.random.uniform(0.6, 1.0)
        })
    suppliers_df = pd.DataFrame(suppliers)
    
    # Shipment Data
    shipments = []
    for i in range(num_shipments):
        supplier_id = np.random.choice(suppliers_df['supplier_id'])
        is_delayed = np.random.choice([0, 1], p=[0.85, 0.15])
        shipments.append({
            'shipment_id': f'SHIP{i:04d}',
            'supplier_id': supplier_id,
            'scheduled_delivery_date': fake.date_this_year(),
            'actual_delivery_date': fake.date_this_year() + pd.to_timedelta(np.random.randint(0, 30) * is_delayed, unit='D'),
        })
    shipments_df = pd.DataFrame(shipments)
    
    # Event Data (simplified for dynamic generation)
    events = []
    for _ in range(num_suppliers // 5):
        events.append({
            'event_type': np.random.choice(['Natural Disaster', 'Geopolitical Conflict', 'Port Closure']),
        })
    events_df = pd.DataFrame(events)

    return suppliers_df, shipments_df, events_df

# --- 3. Dashboard and Analysis ---
def dashboard_page():
    st.title("Supply Chain Risk Analysis Dashboard")
    st.markdown("Use the controls below to **generate a new supply chain simulation** and analyze its key metrics.")

    st.sidebar.header("Simulation Parameters")
    num_suppliers = st.sidebar.slider("Number of Suppliers", 10, 200, 50)
    num_shipments = st.sidebar.slider("Number of Shipments", 100, 2000, 500)
    
    if st.sidebar.button("Run New Simulation"):
        st.session_state['suppliers'], st.session_state['shipments'], st.session_state['events'] = generate_dynamic_data(num_suppliers, num_shipments)
        st.success("New supply chain generated!")
        st.rerun()

    # Initial data generation if not in session state
    if 'suppliers' not in st.session_state:
        st.session_state['suppliers'], st.session_state['shipments'], st.session_state['events'] = generate_dynamic_data(50, 500)
    
    suppliers_df = st.session_state['suppliers']
    shipments_df = st.session_state['shipments']
    events_df = st.session_state['events']

    # Data Preprocessing
    shipments_df['actual_delivery_date'] = pd.to_datetime(shipments_df['actual_delivery_date'])
    shipments_df['scheduled_delivery_date'] = pd.to_datetime(shipments_df['scheduled_delivery_date'])
    shipments_df['delay_days'] = (shipments_df['actual_delivery_date'] - shipments_df['scheduled_delivery_date']).dt.days.fillna(0)
    full_df = pd.merge(shipments_df, suppliers_df, on='supplier_id', how='left')

    # KPI Section
    total_suppliers = suppliers_df.shape[0]
    avg_on_time_rate = suppliers_df['historical_on_time_rate'].mean() * 100
    total_shipments = shipments_df.shape[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Suppliers", value=total_suppliers)
    with col2:
        st.metric(label="Avg. On-Time Rate", value=f"{avg_on_time_rate:.1f}%")
    with col3:
        st.metric(label="Total Shipments", value=total_shipments)

    st.write("---")

    # Supplier Performance Chart
    st.header("Supplier Performance")
    worst_suppliers = suppliers_df.sort_values('historical_on_time_rate').head(10)
    fig_suppliers = go.Figure()
    fig_suppliers.add_trace(go.Bar(
        x=worst_suppliers['supplier_id'],
        y=worst_suppliers['historical_on_time_rate'],
        marker_color='red'
    ))
    st.plotly_chart(fig_suppliers, use_container_width=True)

    # Risk & Events Section
    st.header("Risk & Event Analysis")
    fig_events = px.bar(events_df, x='event_type', title='Distribution of Simulated Risk Events')
    st.plotly_chart(fig_events, use_container_width=True)

    # Scenario Planning
    st.write("---")
    st.header("Scenario Planning: What If?")
    supplier_to_test = st.selectbox("Select a Supplier to simulate a delay:", suppliers_df['supplier_id'].unique())
    delay_days = st.slider("Simulated Delay (Days)", 0, 30, 5)

    if st.button("Run Scenario"):
        avg_delay_for_supplier = full_df[full_df['supplier_id'] == supplier_to_test]['delay_days'].mean()
        new_avg_delay = avg_delay_for_supplier + delay_days
        st.success(f"Simulating a {delay_days}-day delay for {supplier_to_test}.")
        st.info(f"The average delay for this supplier would increase from {avg_delay_for_supplier:.2f} days to {new_avg_delay:.2f} days.")

# --- 4. Application Flow Control ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Login/Sign Up", "Dashboard"])

if st.session_state["authenticated"]:
    st.sidebar.write(f"Logged in as **{st.session_state['username']}**")
    logout_button()
    if page == "Dashboard":
        dashboard_page()
else:
    st.title("Welcome to Supply Chain Risk Analysis")
    st.markdown("Please log in or sign up to access the dashboard.")
    if page == "Login/Sign Up":
        st.sidebar.subheader("Action")
        auth_action = st.sidebar.radio("Choose Action", ["Login", "Sign Up"])
        if auth_action == "Login":
            login_page()
        else:
            signup_page()
    else:
        st.warning("You must be logged in to view the dashboard.")
        st.info("Please navigate to the Login/Sign Up page on the sidebar.")