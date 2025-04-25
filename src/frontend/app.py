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
    selected_tab = st.radio("Select Section", tabs, index=tabs.index(st.session_state.current_tab))
    st.session_state.current_tab = selected_tab
    
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
        st.session_state.current_tab = "Rental Units"
        st.experimental_rerun()

elif st.session_state.current_tab == "Rental Units":
    if not st.session_state.current_property:
        st.warning("Please enter property details first.")
        st.session_state.current_tab = "Property Input"
        st.experimental_rerun()
    
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
            st.experimental_rerun()
    
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
        st.session_state.current_tab = "Financing"
        st.experimental_rerun()

elif st.session_state.current_tab == "Financing":
    if not st.session_state.current_property:
        st.warning("Please enter property details first.")
        st.session_state.current_tab = "Property Input"
        st.experimental_rerun()
    
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
        st.session_state.current_tab = "Expenses & Tax"
        st.experimental_rerun()

elif st.session_state.current_tab == "Expenses & Tax":
    if not st.session_state.current_property or not st.session_state.units:
        st.warning("Please enter property and rental unit details first.")
        st.session_state.current_tab = "Property Input"
        st.experimental_rerun()
    
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
    expense_df["Amount"] = expense_df["Amount"].apply(lambda x: f"{x:.2f}%" if isinstance(x, str) else f"€{x:,.2f}")
    
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
    
    with col2:
        marginal_tax_rate = st.number_input("Your Marginal Tax Rate (%)", min_value=0.0, max_value=100.0, value=42.0)
        property_age = datetime.now().year - st.session_state.current_property.get("year_built", 2000)
        
        # Calculate depreciation rate
        depreciation_rate = 0.025 if property_age > 18 else 0.02  # 2.5% for older buildings, 2% for newer ones
        
        st.markdown(f"**Property Age**: {property_age} years")
        st.markdown(f"**Depreciation Rate**: {depreciation_rate*100:.1f}%")
    
    # Calculate tax benefits
    annual_depreciation = building_value * depreciation_rate
    
    # Get loan details from financing
    loan_amount = st.session_state.financing_data.get("loan_amount", 0) if hasattr(st.session_state, "financing_data") else 0
    interest_rate = st.session_state.financing_data.get("interest_rate", 0) if hasattr(st.session_state, "financing_data") else 0
    
    annual_interest = loan_amount * (interest_rate / 100)
    
    total_deductible = annual_depreciation + annual_interest
    tax_savings = total_deductible * (marginal_tax_rate / 100)
    
    # Display tax benefits
    st.markdown("### Tax Benefit Summary")
    tax_data = [
        ("Annual Depreciation", annual_depreciation),
        ("Annual Interest Expense", annual_interest),
        ("Total Deductible Expenses", total_deductible),
        ("Annual Tax Savings", tax_savings),
        ("Monthly Tax Savings", tax_savings / 12)
    ]
    
    tax_df = pd.DataFrame(tax_data, columns=["Item", "Amount"])
    tax_df["Amount"] = tax_df["Amount"].apply(lambda x: f"€{x:,.2f}")
    
    st.table(tax_df)
    
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
            
            st.session_state.current_tab = "Analysis Results"
            st.experimental_rerun()

elif st.session_state.current_tab == "Analysis Results":
    if not st.session_state.analysis_result:
        st.warning("Please complete all previous steps to generate analysis results.")
        st.session_state.current_tab = "Property Input"
        st.experimental_rerun()
    
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
    coc_return = summary.get("cash_on_cash", 0)
    
    st.markdown("### Investment Assessment")
    
    if cash_flow > 500 and coc_return > 8:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("#### Strong Investment Opportunity")
        st.markdown("This property appears to be an excellent investment with strong cash flow and returns.")
        st.markdown('</div>', unsafe_allow_html=True)
    elif cash_flow > 0 and coc_return > 5:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("#### Solid Investment Opportunity")
        st.markdown("This property appears to be a solid investment with positive cash flow and reasonable returns.")
        st.markdown('</div>', unsafe_allow_html=True)
    elif cash_flow > 0:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("#### Marginal Investment Opportunity")
        st.markdown("This property has positive cash flow but relatively low returns. Consider negotiating a better purchase price or finding ways to increase rental income.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="risk-box">', unsafe_allow_html=True)
        st.markdown("#### Risky Investment")
        st.markdown("This property has negative cash flow. It may be a speculative investment dependent on appreciation, which carries higher risk.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Results
    st.markdown("### Detailed Results")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Cash Flow", "Investment Metrics", "Financing", "Expenses"])
    
    with tab1:
        # Cash flow analysis
        cash_flow_data = analysis.get("cash_flow", {})
        
        # Create cash flow chart
        fig = create_cash_flow_chart(cash_flow_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Cash flow details
        st.markdown("#### Cash Flow Details")
        
        cash_flow_details = [
            ("Monthly Income", cash_flow_data.get("monthly_income", 0)),
            ("Monthly Expenses", cash_flow_data.get("monthly_expenses", 0)),
            ("Monthly Mortgage", cash_flow_data.get("monthly_mortgage", 0)),
            ("Net Operating Income (NOI)", cash_flow_data.get("monthly_noi", 0)),
            ("Cash Flow Before Tax", cash_flow_data.get("monthly_cash_flow_before_tax", 0)),
            ("Monthly Tax Savings", cash_flow_data.get("monthly_tax_savings", 0)),
            ("Cash Flow After Tax", cash_flow_data.get("monthly_cash_flow_after_tax", 0)),
            ("Annual Cash Flow", cash_flow_data.get("annual_cash_flow_after_tax", 0))
        ]
        
        cf_df = pd.DataFrame(cash_flow_details, columns=["Item", "Amount"])
        cf_df["Amount"] = cf_df["Amount"].apply(lambda x: format_currency(x))
        
        st.table(cf_df)
    
    with tab2:
        # Investment metrics
        metrics_data = analysis.get("metrics", {})
        
        # Create ROI metrics chart
        fig = create_roi_chart(metrics_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Investment details
        st.markdown("#### Investment Details")
        
        investment_details = [
            ("Total Investment", metrics_data.get("total_investment", 0)),
            ("Total Cash Invested", metrics_data.get("total_cash_invested", 0)),
            ("Cap Rate", f"{metrics_data.get('cap_rate_percentage', 0):.2f}%"),
            ("Cash-on-Cash Return", f"{metrics_data.get('cash_on_cash_percentage', 0):.2f}%"),
            ("ROI", f"{metrics_data.get('roi_percentage', 0):.2f}%")
        ]
        
        inv_df = pd.DataFrame(investment_details, columns=["Metric", "Value"])
        inv_df["Value"] = inv_df["Value"].apply(lambda x: x if isinstance(x, str) else format_currency(x))
        
        st.table(inv_df)
    
    with tab3:
        # Financing details
        mortgage_data = analysis.get("mortgage", {})
        
        # Create amortization chart
        fig = create_amortization_chart(mortgage_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Financing details
        st.markdown("#### Financing Details")
        
        financing_details = [
            ("Loan Amount", mortgage_data.get("loan_amount", 0)),
            ("Interest Rate", f"{mortgage_data.get('interest_rate', 0):.2f}%"),
            ("Repayment Rate", f"{mortgage_data.get('repayment_rate', 0):.2f}%"),
            ("Term", f"{mortgage_data.get('term_years', 0)} years"),
            ("Monthly Payment", mortgage_data.get("monthly_payment", 0)),
            ("Annual Payment", mortgage_data.get("annual_payment", 0)),
            ("Total Payments over Term", mortgage_data.get("total_payments", 0)),
            ("Total Interest over Term", mortgage_data.get("total_interest", 0))
        ]
        
        fin_df = pd.DataFrame(financing_details, columns=["Item", "Value"])
        fin_df["Value"] = fin_df["Value"].apply(lambda x: x if isinstance(x, str) else format_currency(x))
        
        st.table(fin_df)
    
    with tab4:
        # Expenses details
        expenses_data = analysis.get("expenses", {})
        income_data = analysis.get("income", {})
        
        # Create expenses pie chart
        expense_items = [
            ("Property Tax", expenses_data.get("property_tax_annual", 0)),
            ("Insurance", expenses_data.get("insurance_annual", 0)),
            ("Maintenance", expenses_data.get("maintenance_annual", 0)),
            ("Management", expenses_data.get("management_annual", 0)),
            ("Reserve Fund", expenses_data.get("reserve_annual", 0)),
            ("Additional", expenses_data.get("additional_annual", 0))
        ]
        
        expense_df = pd.DataFrame(expense_items, columns=["Category", "Amount"])
        fig = px.pie(
            expense_df, 
            values="Amount", 
            names="Category", 
            title="Annual Expenses Breakdown",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Expense details
        st.markdown("#### Expense Details")
        
        expense_details = [
            ("Annual Gross Income", income_data.get("effective_annual_rent", 0)),
            ("Vacancy Loss", income_data.get("vacancy_loss_annual", 0)),
            ("Effective Gross Income", income_data.get("effective_annual_rent", 0)),
            ("Total Annual Expenses", expenses_data.get("total_annual_expenses", 0)),
            ("Expense Ratio", f"{expenses_data.get('expense_ratio', 0) * 100:.2f}%")
        ]
        
        exp_df = pd.DataFrame(expense_details, columns=["Item", "Value"])
        exp_df["Value"] = exp_df["Value"].apply(lambda x: x if isinstance(x, str) else format_currency(x))
        
        st.table(exp_df)
    
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
            st.experimental_rerun()