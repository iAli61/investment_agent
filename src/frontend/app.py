"""
Main Streamlit frontend application for Property Investment Analysis App
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import json
from datetime import datetime, timedelta
import os

# Set page configuration
st.set_page_config(
    page_title="Property Investment Analysis",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Application state
if "current_property" not in st.session_state:
    st.session_state.current_property = None
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Property Input"
if "market_data_task_id" not in st.session_state:
    st.session_state.market_data_task_id = None
if "rent_estimation_task_id" not in st.session_state:
    st.session_state.rent_estimation_task_id = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "units" not in st.session_state:
    st.session_state.units = []
if "tab_change_requested" not in st.session_state:
    st.session_state.tab_change_requested = False

# Helper functions
def fetch_market_data(location, property_type):
    """Fetch market data using AI agent"""
    response = requests.post(
        f"{API_URL}/ai/market-data/",
        json={"location": location, "property_type": property_type}
    )
    data = response.json()
    st.session_state.market_data_task_id = data.get("task_id")
    return data

def get_task_result(task_id):
    """Get result of an AI agent task"""
    response = requests.get(f"{API_URL}/ai/tasks/{task_id}")
    return response.json()

def estimate_rent(location, property_type, size_sqm, num_bedrooms=None, 
                 num_bathrooms=None, features=None, condition="average"):
    """Estimate rent using AI agent"""
    response = requests.post(
        f"{API_URL}/ai/rent-estimation/",
        json={
            "location": location, 
            "property_type": property_type,
            "size_sqm": size_sqm,
            "num_bedrooms": num_bedrooms,
            "num_bathrooms": num_bathrooms,
            "features": features if features else [],
            "condition": condition
        }
    )
    data = response.json()
    st.session_state.rent_estimation_task_id = data.get("task_id")
    return data

def analyze_property(property_data, units_data, financing_data, expenses_data, tax_data):
    """Analyze property investment"""
    response = requests.post(
        f"{API_URL}/properties/1/analyze/",  # Property ID is just a placeholder here
        json={
            "property_data": property_data,
            "units_data": units_data,
            "financing_data": financing_data,
            "expenses_data": expenses_data,
            "tax_data": tax_data
        }
    )
    data = response.json()
    st.session_state.analysis_result = data
    return data

def change_tab(tab_name):
    """Change tab safely without causing recursion"""
    st.session_state.current_tab = tab_name
    st.session_state.tab_change_requested = True
    st.rerun()

def format_currency(value):
    """Format a value as currency"""
    return f"€{value:,.2f}"

def create_cash_flow_chart(cash_flow_data):
    """Create a cash flow chart"""
    # Data for the chart
    income = cash_flow_data.get("monthly_income", 0)
    expenses = abs(cash_flow_data.get("monthly_expenses", 0))
    mortgage = abs(cash_flow_data.get("monthly_mortgage", 0))
    tax_savings = cash_flow_data.get("monthly_tax_savings", 0)
    net_cash_flow = cash_flow_data.get("monthly_cash_flow_after_tax", 0)
    
    # Colors
    colors = {
        "Income": "#4CAF50",  # Green
        "Expenses": "#F44336",  # Red
        "Mortgage": "#FF9800",  # Orange
        "Tax Savings": "#2196F3",  # Blue
        "Net Cash Flow": "#9C27B0"  # Purple
    }
    
    # Create waterfall chart
    fig = go.Figure(go.Waterfall(
        name="Cash Flow",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Income", "Expenses", "Mortgage", "Tax Savings", "Net Cash Flow"],
        y=[income, -expenses, -mortgage, tax_savings, 0],
        text=[format_currency(income), 
              format_currency(expenses), 
              format_currency(mortgage), 
              format_currency(tax_savings), 
              format_currency(net_cash_flow)],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#F44336"}},
        increasing={"marker": {"color": "#4CAF50"}},
        totals={"marker": {"color": "#9C27B0"}}
    ))
    
    fig.update_layout(
        title="Monthly Cash Flow Breakdown",
        showlegend=False,
        height=500
    )
    
    return fig

def create_roi_chart(metrics):
    """Create an ROI metrics chart"""
    # Data for the chart
    cap_rate = metrics.get("cap_rate_percentage", 0)
    cash_on_cash = metrics.get("cash_on_cash_percentage", 0)
    roi = metrics.get("roi_percentage", 0)
    
    # Create bar chart
    fig = go.Figure(go.Bar(
        x=["Cap Rate", "Cash-on-Cash Return", "ROI"],
        y=[cap_rate, cash_on_cash, roi],
        text=[f"{cap_rate:.2f}%", f"{cash_on_cash:.2f}%", f"{roi:.2f}%"],
        textposition="auto",
        marker_color=["#4CAF50", "#2196F3", "#9C27B0"]
    ))
    
    fig.update_layout(
        title="Investment Return Metrics",
        xaxis_title="Metric",
        yaxis_title="Percentage",
        yaxis=dict(ticksuffix="%"),
        height=500
    )
    
    return fig

def create_amortization_chart(mortgage_data):
    """Create amortization schedule chart"""
    if "amortization_schedule" not in mortgage_data:
        return None
    
    amortization = mortgage_data["amortization_schedule"]
    years = [item["year"] for item in amortization]
    remaining_balance = [item["remaining_balance"] for item in amortization]
    interest = [item["interest"] for item in amortization]
    principal = [item["principal"] for item in amortization]
    
    # Create the figure
    fig = go.Figure()
    
    # Add lines
    fig.add_trace(go.Scatter(
        x=years,
        y=remaining_balance,
        mode='lines',
        name='Remaining Balance',
        line=dict(color='#FF9800', width=3)
    ))
    
    # Add stacked bars for interest and principal
    fig.add_trace(go.Bar(
        x=years,
        y=interest,
        name='Interest',
        marker_color='#F44336'
    ))
    
    fig.add_trace(go.Bar(
        x=years,
        y=principal,
        name='Principal',
        marker_color='#4CAF50'
    ))
    
    # Update layout
    fig.update_layout(
        title='Amortization Schedule',
        xaxis_title='Year',
        yaxis_title='Amount (€)',
        barmode='stack',
        height=500
    )
    
    return fig

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f8ff;
        border-left: 5px solid #1E88E5;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #f0fff0;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff8f0;
        border-left: 5px solid #FF9800;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .risk-box {
        background-color: #fff0f0;
        border-left: 5px solid #F44336;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #f5f5f5;
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<div class="main-header">Property Investment Analysis</div>', unsafe_allow_html=True)
st.markdown("Analyze real estate investments with AI-powered insights")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("## Navigation")
    tabs = [
        "Property Input", 
        "Rental Units", 
        "Financing", 
        "Expenses & Tax", 
        "Analysis Results"
    ]
    
    # Only update the tab if it was changed directly in the sidebar
    selected_tab = st.radio("Select Section", tabs, index=tabs.index(st.session_state.current_tab))
    if selected_tab != st.session_state.current_tab and not st.session_state.tab_change_requested:
        st.session_state.current_tab = selected_tab
    
    # Reset the tab change request flag
    if st.session_state.tab_change_requested:
        st.session_state.tab_change_requested = False
    
    st.markdown("---")
    st.markdown("## About")
    st.markdown("""
    This application helps real estate investors analyze properties by:
    
    * Calculating acquisition costs
    * Estimating rental income with AI
    * Analyzing financing options
    * Projecting cash flow and returns
    * Assessing investment risks
    
    Powered by AI agents for real-time market data.
    """)

# Main content
if st.session_state.current_tab == "Property Input":
    st.markdown('<div class="sub-header">Property Details</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        address = st.text_input("Property Address", value="" if not st.session_state.current_property else st.session_state.current_property.get("address", ""))
        property_type = st.selectbox("Property Type", ["apartment", "house", "multi-family", "commercial"], index=0 if not st.session_state.current_property else ["apartment", "house", "multi-family", "commercial"].index(st.session_state.current_property.get("property_type", "apartment")))
        year_built = st.number_input("Year Built", min_value=1800, max_value=datetime.now().year, value=2000 if not st.session_state.current_property else st.session_state.current_property.get("year_built", 2000))
        condition = st.selectbox("Property Condition", ["excellent", "good", "average", "fair", "poor"], index=2 if not st.session_state.current_property else ["excellent", "good", "average", "fair", "poor"].index(st.session_state.current_property.get("condition", "average")))
    
    with col2:
        purchase_price = st.number_input("Purchase Price (€)", min_value=0, value=500000 if not st.session_state.current_property else st.session_state.current_property.get("purchase_price", 500000))
        size_sqm = st.number_input("Property Size (sqm)", min_value=0, value=100 if not st.session_state.current_property else st.session_state.current_property.get("size_sqm", 100))
        num_units = st.number_input("Number of Units", min_value=1, value=1 if not st.session_state.current_property else st.session_state.current_property.get("num_units", 1))
        region = st.selectbox("Region/State", ["berlin", "hamburg", "bayern", "brandenburg"], index=0 if not st.session_state.current_property else ["berlin", "hamburg", "bayern", "brandenburg"].index(st.session_state.current_property.get("region", "berlin")))
    
    # Market Data section
    st.markdown('<div class="sub-header">Market Data</div>', unsafe_allow_html=True)
    st.markdown("Fetch current market data for your target location using our AI agent")
    
    location = st.text_input("Location (City/District)", value="Berlin Mitte" if not st.session_state.current_property else st.session_state.current_property.get("location", "Berlin Mitte"))
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Fetch Market Data"):
            with st.spinner("Gathering market data..."):
                fetch_market_data(location, property_type)
    
    # Check if there's a task running and display results if available
    if st.session_state.market_data_task_id:
        task_result = get_task_result(st.session_state.market_data_task_id)
        
        if task_result.get("status") == "pending" or task_result.get("status") == "running":
            st.info("Gathering market data... (this may take a few moments)")
        
        elif task_result.get("status") == "completed" and "result" in task_result:
            result = task_result.get("result", {})
            if "data" in result and result.get("success", False):
                market_data = result["data"]
                
                # Display market data in a nice format
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.markdown(f"### Market Data for {market_data.get('location')}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Average Price**: €{market_data.get('avg_price_sqm'):,.2f}/sqm")
                with col2:
                    st.markdown(f"**Average Rent**: €{market_data.get('avg_rent_sqm'):,.2f}/sqm")
                with col3:
                    st.markdown(f"**Vacancy Rate**: {market_data.get('vacancy_rate', 0) * 100:.1f}%")
                
                st.markdown(f"**Confidence Level**: {result.get('confidence_level', 0) * 100:.1f}%")
                st.markdown(f"**Data Sources**: {len(market_data.get('sources', []))} sources")
                st.markdown(f"**Last Updated**: {result.get('timestamp', '')[:10]}")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Failed to retrieve market data. Please try again.")
    
    # Save property data
    if st.button("Save Property Details"):
        # Create property data dictionary
        property_data = {
            "address": address,
            "purchase_price": purchase_price,
            "property_type": property_type,
            "year_built": year_built,
            "size_sqm": size_sqm,
            "num_units": num_units,
            "condition_assessment": condition,
            "region": region,
            "location": location,
            "property_age_years": datetime.now().year - year_built
        }
        
        # Store in session state
        st.session_state.current_property = property_data
        
        # In a real app, you would send this to the backend API
        # response = requests.post(f"{API_URL}/properties/", json=property_data)
        # data = response.json()
        
        st.success("Property details saved successfully!")
        change_tab("Rental Units")

elif st.session_state.current_tab == "Rental Units":
    if not st.session_state.current_property:
        st.warning("Please enter property details first.")
        change_tab("Property Input")
    
    st.markdown('<div class="sub-header">Rental Units</div>', unsafe_allow_html=True)
    st.markdown(f"Add rental units for {st.session_state.current_property.get('address', 'your property')}")
    
    # Display existing units in a table
    if st.session_state.units:
        st.markdown("### Current Units")
        units_df = pd.DataFrame(st.session_state.units)
        
        # Format for display
        display_columns = ['unit_number', 'size_sqm', 'num_bedrooms', 'num_bathrooms', 
                           'is_occupied', 'current_rent', 'potential_rent']
        rename_map = {
            'unit_number': 'Unit', 
            'size_sqm': 'Size (sqm)', 
            'num_bedrooms': 'Bedrooms',
            'num_bathrooms': 'Bathrooms', 
            'is_occupied': 'Occupied',
            'current_rent': 'Current Rent (€)', 
            'potential_rent': 'Potential Rent (€)'
        }
        
        if not units_df.empty:
            display_df = units_df[display_columns].rename(columns=rename_map)
            st.dataframe(display_df)
    
    # Add new unit form
    st.markdown("### Add New Unit")
    
    with st.form("new_unit_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            unit_number = st.text_input("Unit Number/Name", "")
            size_sqm = st.number_input("Size (sqm)", min_value=0.0, value=0.0)
            num_bedrooms = st.number_input("Number of Bedrooms", min_value=0, value=1)
            num_bathrooms = st.number_input("Number of Bathrooms", min_value=0.0, value=1.0, step=0.5)
        
        with col2:
            is_occupied = st.checkbox("Currently Occupied")
            current_rent = st.number_input("Current Monthly Rent (€)", min_value=0.0, value=0.0, disabled=not is_occupied)
            potential_rent = st.number_input("Potential Monthly Rent (€)", min_value=0.0, value=0.0)
            
            features = st.multiselect(
                "Features",
                options=["balcony", "garden", "terrace", "parking", "elevator", "furnished", "modern_kitchen", "floor_heating"],
                default=[]
            )
        
        submitted = st.form_submit_button("Add Unit")
        
        if submitted:
            # Create new unit object
            new_unit = {
                "unit_number": unit_number,
                "size_sqm": size_sqm,
                "num_bedrooms": num_bedrooms,
                "num_bathrooms": num_bathrooms,
                "is_occupied": is_occupied,
                "current_rent": current_rent if is_occupied else 0,
                "potential_rent": potential_rent,
                "features": features
            }
            
            # Add to session state
            if "units" not in st.session_state:
                st.session_state.units = []
            
            st.session_state.units.append(new_unit)
            st.success(f"Unit {unit_number} added successfully!")
            st.rerun()
    
    # Rent estimation with AI
    st.markdown('<div class="sub-header">Rent Estimation with AI</div>', unsafe_allow_html=True)
    st.markdown("Estimate potential rent for vacant units using our AI agent")
    
    with st.form("rent_estimation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            unit_size = st.number_input("Unit Size (sqm)", min_value=10.0, value=50.0)
            bedrooms = st.number_input("Bedrooms", min_value=0, value=1)
            bathrooms = st.number_input("Bathrooms", min_value=0.0, value=1.0, step=0.5)
        
        with col2:
            unit_features = st.multiselect(
                "Unit Features",
                options=["balcony", "garden", "terrace", "parking", "elevator", "furnished", "modern_kitchen", "floor_heating"],
                default=[]
            )
            unit_condition = st.selectbox("Unit Condition", ["excellent", "good", "average", "fair", "poor"], index=2)
        
        estimate_submitted = st.form_submit_button("Estimate Rent")
        
        if estimate_submitted:
            with st.spinner("Estimating rent..."):
                location = st.session_state.current_property.get("location", "Berlin")
                property_type = st.session_state.current_property.get("property_type", "apartment")
                
                estimate_rent(
                    location=location,
                    property_type=property_type,
                    size_sqm=unit_size,
                    num_bedrooms=bedrooms,
                    num_bathrooms=bathrooms,
                    features=unit_features,
                    condition=unit_condition
                )
    
    # Check if there's a rent estimation task running and display results
    if st.session_state.rent_estimation_task_id:
        task_result = get_task_result(st.session_state.rent_estimation_task_id)
        
        if task_result.get("status") == "pending" or task_result.get("status") == "running":
            st.info("Estimating rent... (this may take a few moments)")
        
        elif task_result.get("status") == "completed" and "result" in task_result:
            result = task_result.get("result", {})
            if result.get("success", False):
                # Display rent estimate in a nice format
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.markdown("### Rent Estimate")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Estimated Rent**: €{result.get('estimated_rent', 0):,.2f}/month")
                with col2:
                    st.markdown(f"**Rent per sqm**: €{result.get('rent_per_sqm', 0):,.2f}")
                with col3:
                    st.markdown(f"**Confidence**: {result.get('confidence_level', 0) * 100:.1f}%")
                
                # Display rent range
                rent_range = result.get("rent_range", {})
                st.markdown("### Rent Range")
                cols = st.columns(3)
                with cols[0]:
                    st.markdown(f"**Low**: €{rent_range.get('low', 0):,.2f}")
                with cols[1]:
                    st.markdown(f"**Medium**: €{rent_range.get('medium', 0):,.2f}")
                with cols[2]:
                    st.markdown(f"**High**: €{rent_range.get('high', 0):,.2f}")
                
                # Legal warning if applicable
                if result.get("legal_limit_warning", False):
                    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                    st.markdown(f"⚠️ **Legal Limit Warning**: The estimated rent exceeds the legal limit (Mietpreisbremse) of €{result.get('legal_limit', 0):,.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Explanation
                st.markdown("### Explanation")
                st.markdown(result.get("explanation", ""))
                
                # Comparable properties if available
                if "comparable_properties" in result and result["comparable_properties"]:
                    st.markdown("### Comparable Properties")
                    comp_df = pd.DataFrame(result["comparable_properties"])
                    display_cols = ["address", "size_sqm", "bedrooms", "rent", "rent_per_sqm", "distance_km"]
                    rename_map = {
                        "address": "Address",
                        "size_sqm": "Size (sqm)",
                        "bedrooms": "Bedrooms",
                        "rent": "Rent (€)",
                        "rent_per_sqm": "€/sqm",
                        "distance_km": "Distance (km)"
                    }
                    st.dataframe(comp_df[display_cols].rename(columns=rename_map))
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Failed to estimate rent. Please try again.")
    
    # Navigate to next section
    if st.button("Continue to Financing"):
        change_tab("Financing")

elif st.session_state.current_tab == "Financing":
    if not st.session_state.current_property:
        st.warning("Please enter property details first.")
        change_tab("Property Input")
    
    st.markdown('<div class="sub-header">Financing Details</div>', unsafe_allow_html=True)
    st.markdown(f"Set up financing for {st.session_state.current_property.get('address', 'your property')}")
    
    # Property price info
    purchase_price = st.session_state.current_property.get("purchase_price", 0)
    st.markdown(f"**Purchase Price**: €{purchase_price:,.2f}")
    
    # Calculate closing costs
    region = st.session_state.current_property.get("region", "berlin")
    
    # Regional property transfer tax rates
    transfer_tax_rates = {
        "berlin": 0.06,
        "hamburg": 0.045,
        "bayern": 0.035,
        "brandenburg": 0.065,
    }
    transfer_tax_rate = transfer_tax_rates.get(region.lower(), 0.05)
    
    # Calculate costs
    transfer_tax = purchase_price * transfer_tax_rate
    notary_fee = purchase_price * 0.015
    land_registry = purchase_price * 0.005
    agent_fee = purchase_price * 0.0357
    
    # Total closing costs
    closing_costs = transfer_tax + notary_fee + land_registry + agent_fee
    total_acquisition_cost = purchase_price + closing_costs
    
    # Display closing costs breakdown
    st.markdown("### Closing Costs Breakdown")
    
    closing_costs_data = [
        ("Transfer Tax", transfer_tax, f"{transfer_tax_rate*100:.1f}%"),
        ("Notary Fee", notary_fee, "1.5%"),
        ("Land Registry", land_registry, "0.5%"),
        ("Agent Fee", agent_fee, "3.57%"),
        ("Total Closing Costs", closing_costs, f"{closing_costs/purchase_price*100:.2f}%"),
        ("Total Acquisition Cost", total_acquisition_cost, "")
    ]
    
    costs_df = pd.DataFrame(closing_costs_data, columns=["Item", "Amount", "Percentage"])
    
    # Format currency
    costs_df["Amount"] = costs_df["Amount"].apply(lambda x: f"€{x:,.2f}")
    
    st.table(costs_df)
    
    # Financing form
    st.markdown("### Financing Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        available_cash = st.number_input("Available Cash (€)", min_value=0.0, value=0.0)
        down_payment_percentage = st.slider("Down Payment Percentage", min_value=0, max_value=100, value=20)
        
        # Calculate down payment and required cash
        down_payment = purchase_price * (down_payment_percentage / 100)
        required_cash = down_payment + closing_costs
        loan_amount = purchase_price - down_payment
        
        # Check if enough cash is available
        cash_shortage = max(0, required_cash - available_cash)
        has_enough_cash = available_cash >= required_cash
        
        # Display calculations
        st.markdown(f"**Down Payment Amount**: €{down_payment:,.2f}")
        st.markdown(f"**Required Cash** (Down Payment + Closing Costs): €{required_cash:,.2f}")
        
        if not has_enough_cash:
            st.warning(f"Cash Shortage: €{cash_shortage:,.2f}")
    
    with col2:
        interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=20.0, value=3.5, step=0.1)
        repayment_rate = st.number_input("Repayment Rate/Tilgung (%)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
        term_years = st.number_input("Loan Term (Years)", min_value=5, max_value=40, value=30)
        
        # Calculate monthly payment
        total_rate = (interest_rate + repayment_rate) / 100
        monthly_rate = total_rate / 12
        monthly_payment = loan_amount * monthly_rate
        
        # Display payment details
        st.markdown(f"**Loan Amount**: €{loan_amount:,.2f}")
        st.markdown(f"**Monthly Payment**: €{monthly_payment:,.2f}")
        st.markdown(f"**Annual Payment**: €{monthly_payment*12:,.2f}")
    
    # Save financing information
    if st.button("Save Financing Details"):
        financing_data = {
            "available_cash": available_cash,
            "down_payment_percentage": down_payment_percentage,
            "interest_rate": interest_rate,
            "repayment_rate": repayment_rate,
            "term_years": term_years,
            "loan_amount": loan_amount,
            "monthly_payment": monthly_payment
        }
        
        # Store in session state
        st.session_state.financing_data = financing_data
        
        st.success("Financing details saved successfully!")
        change_tab("Expenses & Tax")

elif st.session_state.current_tab == "Expenses & Tax":
    if not st.session_state.current_property or not st.session_state.units:
        st.warning("Please enter property and rental unit details first.")
        change_tab("Property Input")
    
    st.markdown('<div class="sub-header">Operating Expenses & Tax Benefits</div>', unsafe_allow_html=True)
    
    # Calculate potential rental income
    units = st.session_state.units
    current_rent = sum(unit.get("current_rent", 0) for unit in units if unit.get("is_occupied", False))
    potential_rent = sum(
        unit.get("current_rent", 0) if unit.get("is_occupied", False) else unit.get("potential_rent", 0)
        for unit in units
    )
    
    # Display rental income
    st.markdown("### Rental Income")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Current Monthly Rent**: €{current_rent:,.2f}")
    with col2:
        st.markdown(f"**Potential Monthly Rent**: €{potential_rent:,.2f}")
    with col3:
        st.markdown(f"**Potential Annual Rent**: €{potential_rent*12:,.2f}")
    
    # Operating Expenses
    st.markdown("### Operating Expenses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        property_tax = st.number_input("Annual Property Tax (€)", min_value=0.0, value=potential_rent*12*0.01)
        insurance = st.number_input("Annual Insurance (€)", min_value=0.0, value=potential_rent*12*0.005)
        
    with col2:
        maintenance_percentage = st.number_input("Maintenance (% of Rent)", min_value=0.0, max_value=100.0, value=10.0)
        management_percentage = st.number_input("Property Management (% of Rent)", min_value=0.0, max_value=100.0, value=5.0)
        reserve_percentage = st.number_input("Reserve Fund (% of Rent)", min_value=0.0, max_value=100.0, value=3.0)
    
    # Calculate expenses
    maintenance = potential_rent * 12 * (maintenance_percentage / 100)
    management = potential_rent * 12 * (management_percentage / 100)
    reserve = potential_rent * 12 * (reserve_percentage / 100)
    
    total_expenses = property_tax + insurance + maintenance + management + reserve
    expense_ratio = total_expenses / (potential_rent * 12) if potential_rent > 0 else 0
    
    # Display expense summary
    st.markdown("### Expense Summary")
    expense_data = [
        ("Property Tax", property_tax),
        ("Insurance", insurance),
        ("Maintenance", maintenance),
        ("Property Management", management),
        ("Reserve Fund", reserve),
        ("Total Annual Expenses", total_expenses),
        ("Monthly Expenses", total_expenses / 12),
        ("Expense Ratio", f"{expense_ratio*100:.2f}%")
    ]
    
    expense_df = pd.DataFrame(expense_data, columns=["Expense", "Amount"])
    # Fix the lambda function logic - only apply float formatting to non-string values
    expense_df["Amount"] = expense_df["Amount"].apply(lambda x: x if isinstance(x, str) else f"€{x:,.2f}")
    
    st.table(expense_df)
    
    # Tax Benefits
    st.markdown("### Tax Benefits")
    
    col1, col2 = st.columns(2)
    
    with col1:
        building_percentage = st.slider("Building Value (% of Purchase Price)", min_value=50, max_value=90, value=70)
        purchase_price = st.session_state.current_property.get("purchase_price", 0)
        building_value = purchase_price * (building_percentage / 100)
        land_value = purchase_price - building_value
        
        st.markdown(f"**Building Value**: €{building_value:,.2f}")
        st.markdown(f"**Land Value**: €{land_value:,.2f}")
        
        # Add additional Werbungskosten input
        additional_werbungskosten = st.number_input("Additional Werbungskosten (€)", 
                                                   min_value=0.0, 
                                                   max_value=50000.0, 
                                                   value=0.0,
                                                   help="Additional income-related expenses beyond standard allowance")
    
    with col2:
        marginal_tax_rate = st.number_input("Your Marginal Tax Rate (%)", min_value=0.0, max_value=100.0, value=42.0)
        property_age = datetime.now().year - st.session_state.current_property.get("year_built", 2000)
        
        # Calculate depreciation rate
        depreciation_rate = 0.025 if property_age > 18 else 0.02  # 2.5% for older buildings, 2% for newer ones
        
        st.markdown(f"**Property Age**: {property_age} years")
        st.markdown(f"**Depreciation Rate**: {depreciation_rate*100:.1f}%")
        
        # Add option for progressive tax calculation
        use_progressive_tax = st.checkbox("Use Progressive Tax Calculation", value=False,
                                        help="Calculate tax benefits using German tax brackets instead of flat rate")
        if use_progressive_tax:
            other_income = st.number_input("Your Other Annual Income (€)", 
                                         min_value=0.0, 
                                         max_value=1000000.0, 
                                         value=60000.0)
    
    # Get operating expenses for tax calculation
    annual_expenses = total_expenses
    
    # Calculate tax benefits
    # Get loan details from financing
    loan_amount = st.session_state.financing_data.get("loan_amount", 0) if hasattr(st.session_state, "financing_data") else 0
    interest_rate = st.session_state.financing_data.get("interest_rate", 0) if hasattr(st.session_state, "financing_data") else 0
    
    # Prepare parameters for enhanced tax calculation
    tax_params = {
        "building_value": building_value,
        "loan_amount": loan_amount,
        "interest_rate": interest_rate,
        "marginal_tax_rate": marginal_tax_rate,
        "property_age_years": property_age,
        "annual_operating_expenses": annual_expenses,
        "additional_werbungskosten": additional_werbungskosten,
        "use_progressive_tax": use_progressive_tax,
        "other_income": other_income if use_progressive_tax else 0
    }
    
    # Import the calculate_tax_benefits function directly
    from src.utils.financial_utils import calculate_tax_benefits
    
    # Calculate tax benefits with enhanced German tax logic
    tax_benefits_result = calculate_tax_benefits(**tax_params)
    
    annual_depreciation = tax_benefits_result["annual_depreciation"]
    annual_interest = tax_benefits_result["annual_interest_expense"]
    standard_werbungskosten = tax_benefits_result["standard_werbungskosten"]
    total_werbungskosten = tax_benefits_result["total_werbungskosten"]
    werbungskosten_above_standard = tax_benefits_result["werbungskosten_above_standard"]
    total_deductible = tax_benefits_result["total_deductible_expenses"]
    tax_savings = tax_benefits_result["annual_tax_savings"]
    effective_tax_rate = tax_benefits_result["effective_tax_rate"]
    
    # Display tax benefits
    st.markdown("### Tax Benefit Summary")
    tax_data = [
        ("Annual Depreciation (AfA)", annual_depreciation),
        ("Annual Interest Expense", annual_interest),
        ("Standard Werbungskosten Allowance", standard_werbungskosten),
        ("Total Werbungskosten", total_werbungskosten),
        ("Additional Deductible Werbungskosten", werbungskosten_above_standard),
        ("Total Deductible Expenses", total_deductible),
        ("Annual Tax Savings", tax_savings),
        ("Monthly Tax Savings", tax_savings / 12),
        ("Effective Tax Rate", f"{effective_tax_rate:.2f}%")
    ]
    tax_df = pd.DataFrame(tax_data, columns=["Item", "Amount"])
    # Apply formatting except for the percentage value
    tax_df["Amount"] = tax_df.apply(lambda row: row["Amount"] if isinstance(row["Amount"], str) else f"€{row['Amount']:,.2f}", axis=1)
    
    st.table(tax_df)
    
    # Visualizations
    st.markdown("### Tax Benefit Visualizations")
    
    tab1, tab2 = st.tabs(["Werbungskosten Impact", "Tax Rate Impact"])
    
    with tab1:
        # Get visualization data
        werbungskosten_data = tax_benefits_result["visualization_data"]["werbungskosten_impact"]
        
        # Convert to DataFrame for plotting
        wk_df = pd.DataFrame(werbungskosten_data)
        
        # Create the figure
        fig = go.Figure()
        
        # Add trace for tax savings
        fig.add_trace(go.Scatter(
            x=wk_df["werbungskosten"],
            y=wk_df["tax_savings"],
            mode='lines+markers',
            name='Tax Savings',
            line=dict(color='#4CAF50', width=3)
        ))
        
        # Add trace for total deductible
        fig.add_trace(go.Scatter(
            x=wk_df["werbungskosten"],
            y=wk_df["total_deductible"],
            mode='lines',
            name='Total Deductible',
            line=dict(color='#2196F3', width=2, dash='dash')
        ))
        
        # Update layout
        fig.update_layout(
            title='Impact of Additional Werbungskosten on Tax Benefits',
            xaxis_title='Additional Werbungskosten (€)',
            yaxis_title='Amount (€)',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        This chart shows how increasing your additional Werbungskosten (income-related expenses) 
        impacts your total tax deductions and tax savings. The standard Werbungskosten allowance 
        (€1,000) is automatically applied if you don't have higher expenses.
        """)
    
    with tab2:
        # Get visualization data
        tax_rate_data = tax_benefits_result["visualization_data"]["tax_rate_impact"]
        
        # Convert to DataFrame for plotting
        tr_df = pd.DataFrame(tax_rate_data)
        
        # Create the figure
        fig = go.Figure()
        
        # Add trace for tax savings
        fig.add_trace(go.Bar(
            x=tr_df["tax_rate"],
            y=tr_df["tax_savings"],
            marker_color='#9C27B0',
            name='Tax Savings'
        ))
        
        # Add vertical line for current tax rate
        fig.add_shape(
            type="line",
            x0=marginal_tax_rate, x1=marginal_tax_rate,
            y0=0, y1=tr_df["tax_savings"].max() * 1.1,
            line=dict(color="red", width=2, dash="dash")
        )
        
        # Add annotation for current tax rate
        fig.add_annotation(
            x=marginal_tax_rate,
            y=tr_df["tax_savings"].max() * 1.05,
            text=f"Your Tax Rate: {marginal_tax_rate}%",
            showarrow=True,
            arrowhead=1,
            ax=50,
            ay=-40
        )
        
        # Update layout
        fig.update_layout(
            title='Impact of Marginal Tax Rate on Annual Tax Savings',
            xaxis_title='Marginal Tax Rate (%)',
            xaxis=dict(ticksuffix="%"),
            yaxis_title='Annual Tax Savings (€)',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        This chart shows how your marginal tax rate affects your annual tax savings from this property investment.
        In Germany, higher income investors typically benefit more from real estate tax advantages due to the 
        progressive tax system.
        """)
    
    # Explanation of German tax benefits for real estate
    with st.expander("Learn more about German Tax Benefits for Real Estate"):
        st.markdown("""
        ### Understanding German Tax Benefits for Real Estate Investments
        
        Real estate investments in Germany offer several tax advantages:
        
        1. **Depreciation (AfA)**: You can deduct the building's value (not land) as an expense over time:
           - 2% per year for buildings constructed after 2007 (50-year period)
           - 2.5% per year for buildings constructed before 2007 (40-year period)
           - Up to 4% for historical or protected buildings
        
        2. **Interest Deduction**: Interest paid on mortgage loans is fully deductible from rental income.
        
        3. **Werbungskosten**: All expenses related to generating rental income are deductible, including:
           - Property management fees
           - Maintenance and repairs
           - Insurance premiums
           - Property tax
           - Travel costs for property visits
           - Legal and accounting fees
        
        4. **Standard Allowance**: If your actual Werbungskosten are below €1,000, you can still claim the standard allowance.
        
        5. **Loss Offsetting**: Negative rental income can offset other income sources, reducing your overall tax burden.
        
        The German tax system is progressive, so the higher your income tax rate, the more valuable these deductions become.
        """)
    
    # Save expenses and tax data
    if st.button("Save Expenses & Tax Details"):
        expenses_data = {
            "property_tax": property_tax,
            "insurance": insurance,
            "maintenance_percentage": maintenance_percentage,
            "management_percentage": management_percentage,
            "reserve_percentage": reserve_percentage,
            "total_annual_expenses": total_expenses,
            "monthly_expenses": total_expenses / 12,
            "expense_ratio": expense_ratio
        }
        
        tax_data = {
            "building_value": building_value,
            "land_value": land_value,
            "marginal_tax_rate": marginal_tax_rate,
            "annual_depreciation": annual_depreciation,
            "annual_interest": annual_interest,
            "total_deductible": total_deductible,
            "annual_tax_savings": tax_savings,
            "monthly_tax_savings": tax_savings / 12
        }
        
        # Store in session state
        st.session_state.expenses_data = expenses_data
        st.session_state.tax_data = tax_data
        
        st.success("Expenses and tax details saved successfully!")
        
        # Run analysis
        with st.spinner("Analyzing investment..."):
            # Prepare data for analysis
            property_data = st.session_state.current_property
            units_data = st.session_state.units
            financing_data = st.session_state.financing_data
            expenses_data = st.session_state.expenses_data
            tax_data = st.session_state.tax_data
            
            # Run analysis
            analysis_result = analyze_property(
                property_data, units_data, financing_data, expenses_data, tax_data
            )
            
            st.session_state.analysis_result = analysis_result
            
            change_tab("Analysis Results")

elif st.session_state.current_tab == "Analysis Results":
    if not st.session_state.analysis_result:
        st.warning("Please complete all previous steps to generate analysis results.")
        change_tab("Property Input")
    
    st.markdown('<div class="sub-header">Investment Analysis Results</div>', unsafe_allow_html=True)
    
    # Get analysis data
    analysis = st.session_state.analysis_result
    
    # Show summary metrics
    summary = analysis.get("analysis_summary", {})
    
    st.markdown("### Summary Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{format_currency(summary.get("monthly_cash_flow", 0))}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Monthly Cash Flow</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{summary.get("cap_rate", 0):.2f}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Cap Rate</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{summary.get("cash_on_cash", 0):.2f}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Cash-on-Cash Return</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{summary.get("roi", 0):.2f}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">ROI</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display investment assessment
    cash_flow = summary.get("monthly_cash_flow", 0)
    annual_cash_flow = summary.get("annual_cash_flow", 0)
    coc_return = summary.get("cash_on_cash", 0)
    cap_rate = summary.get("cap_rate", 0)
    
    # Get additional details for more accurate assessment
    mortgage_data = analysis.get("mortgage", {})
    tax_benefits = analysis.get("tax_benefits", {})
    financing = analysis.get("financing", {})
    metrics = analysis.get("metrics", {})
    
    # Extract the total cash invested and loan details
    loan_amount = mortgage_data.get("loan_amount", 0)
    total_investment = metrics.get("total_investment", 0)
    total_cash_invested = metrics.get("total_cash_invested", 0)
    monthly_tax_savings = tax_benefits.get("monthly_tax_savings", 0) if tax_benefits else 0
    leverage_ratio = loan_amount / total_investment if total_investment > 0 else 0
    debt_service_coverage_ratio = summary.get("monthly_cash_flow", 0) / mortgage_data.get("monthly_payment", 1) if mortgage_data.get("monthly_payment", 0) > 0 else 0
    
    st.markdown("### Investment Assessment")
    
    # More nuanced assessment logic based on German investment criteria
    if cash_flow > 1000 and coc_return > 7 and cap_rate > 4:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("#### Excellent Investment Opportunity")
        st.markdown(f"""
        This property offers strong positive cash flow of {format_currency(cash_flow)}/month with an attractive cash-on-cash return of {coc_return:.2f}%. 
        
        **Key Strengths:**
        - Strong monthly cash flow: {format_currency(cash_flow)}
        - Excellent cash-on-cash return: {coc_return:.2f}%
        - Solid cap rate: {cap_rate:.2f}%
        - Tax benefits contribute significantly: {format_currency(monthly_tax_savings)}/month
        
        This investment meets the criteria for a high-performing German property investment with excellent tax advantages and strong rental income relative to expenses.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif cash_flow > 300 and coc_return > 5 and cap_rate > 3.5:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("#### Strong Investment Opportunity")
        st.markdown(f"""
        This property offers good positive cash flow of {format_currency(cash_flow)}/month with a good cash-on-cash return of {coc_return:.2f}%.
        
        **Key Strengths:**
        - Good monthly cash flow: {format_currency(cash_flow)}
        - Solid cash-on-cash return: {coc_return:.2f}%
        - Acceptable cap rate: {cap_rate:.2f}%
        - Monthly tax benefit: {format_currency(monthly_tax_savings)}
        
        The property demonstrates solid investment characteristics with good tax benefits and positive cash flow typical of a successful German rental property.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif cash_flow > 0 and coc_return > 3:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("#### Decent Investment Opportunity with Potential")
        st.markdown(f"""
        This property offers modest positive cash flow of {format_currency(cash_flow)}/month with an acceptable cash-on-cash return of {coc_return:.2f}%.
        
        **Considerations:**
        - Modest monthly cash flow: {format_currency(cash_flow)}
        - Moderate cash-on-cash return: {coc_return:.2f}%
        - Cap rate: {cap_rate:.2f}%
        - Tax benefits help improve returns: {format_currency(monthly_tax_savings)}/month
        
        This investment offers positive cash flow, but returns are lower than ideal. Consider:
        - Negotiating a better purchase price
        - Finding ways to increase rental income
        - Improving tax efficiency through additional Werbungskosten
        - Adjusting financing terms for better cash flow
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif cash_flow > -200 and monthly_tax_savings > abs(cash_flow):
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("#### Tax-Advantaged Investment")
        st.markdown(f"""
        This property has slightly negative cash flow of {format_currency(cash_flow)}/month, but significant tax advantages help offset this.
        
        **Key Considerations:**
        - Slightly negative monthly cash flow: {format_currency(cash_flow)}
        - Important tax benefits: {format_currency(monthly_tax_savings)}/month
        - Cash-on-cash return: {coc_return:.2f}%
        - Cap rate: {cap_rate:.2f}%
        
        This is a common scenario for German property investments where tax benefits are the primary advantage. The property may become cash-flow positive as:
        - Rents increase over time
        - Mortgage is paid down
        - You optimize your tax situation further
        
        This investment might still make sense for high-income investors seeking tax advantages, but carries more risk than cash-flow positive properties.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.markdown('<div class="risk-box">', unsafe_allow_html=True)
        st.markdown("#### High-Risk Investment")
        st.markdown(f"""
        This property has significant negative cash flow of {format_currency(cash_flow)}/month, which is not offset by tax benefits.
        
        **Risk Factors:**
        - Negative monthly cash flow: {format_currency(cash_flow)}
        - Tax benefits: {format_currency(monthly_tax_savings)}/month
        - Cash-on-cash return: {coc_return:.2f}%
        
        This is a speculative investment dependent on:
        - Significant future appreciation
        - Substantial rental income growth
        - Refinancing to better terms in the future
        
        Consider revisiting your assumptions, negotiating a lower purchase price, improving financing terms, or seeking an alternative property with better fundamentals.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Add a debt service coverage ratio assessment
    st.markdown("### Risk Assessment")
    
    # Calculate debt service coverage ratio (DSCR)
    noi = analysis.get("cash_flow", {}).get("monthly_noi", 0)
    debt_service = mortgage_data.get("monthly_payment", 0)
    dscr = noi / debt_service if debt_service > 0 else float('inf')
    
    dscr_col1, dscr_col2, dscr_col3 = st.columns(3)
    
    with dscr_col1:
        st.metric("Debt Service Coverage Ratio", f"{dscr:.2f}x", 
                 delta="Good" if dscr >= 1.25 else ("Acceptable" if dscr >= 1.0 else "Poor"))
    
    with dscr_col2:
        loan_to_value = leverage_ratio * 100
        st.metric("Loan-to-Value Ratio", f"{loan_to_value:.1f}%", 
                 delta="Low Risk" if loan_to_value <= 60 else ("Medium Risk" if loan_to_value <= 80 else "High Risk"))
    
    with dscr_col3:
        # Calculate break-even occupancy
        expenses = analysis.get("expenses", {})
        income = analysis.get("income", {})
        
        monthly_expenses = expenses.get("total_monthly_expenses", 0)
        monthly_mortgage = mortgage_data.get("monthly_payment", 0)
        potential_monthly_rent = income.get("potential_monthly_rent", 1)
        
        break_even_occupancy = ((monthly_expenses + monthly_mortgage) / potential_monthly_rent) * 100 if potential_monthly_rent > 0 else 100
        
        st.metric("Break-even Occupancy", f"{min(break_even_occupancy, 100):.1f}%", 
                 delta="Low Risk" if break_even_occupancy <= 70 else ("Medium Risk" if break_even_occupancy <= 85 else "High Risk"))
    
    # Add some risk analysis text
    if dscr < 1.0:
        st.markdown('<div class="risk-box">', unsafe_allow_html=True)
        st.markdown("""
        **Warning: Low Debt Service Coverage Ratio**
        
        Your property's income is not sufficient to cover the debt payments. This increases the risk of financial distress if there are vacancies or unexpected expenses.
        Consider increasing rental income, reducing expenses, or improving loan terms.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    elif break_even_occupancy > 85:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        **Caution: High Break-even Occupancy**
        
        Your property needs high occupancy to break even. This increases vulnerability to market downturns or periods of vacancy.
        Consider strategies to increase rental income or reduce financing costs.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# Footer or next steps can be added here if needed
# Provide options to download reports, save the project, or start a new analysis

    # Next Steps
    st.markdown("### Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate Full Report"):
            st.info("This feature would generate a downloadable PDF report with all analysis details.")
    
    with col2:
        if st.button("Start New Analysis"):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            st.session_state.current_tab = "Property Input"
            st.rerun()