"""
Utilities for property investment financial calculations
"""
from typing import Dict, Any, List, Optional, Tuple
import math


def calculate_total_acquisition_cost(purchase_price: float, 
                                     region: str = "berlin") -> Dict[str, float]:
    """
    Calculate the total acquisition cost including closing costs
    
    Args:
        purchase_price: The purchase price of the property
        region: The region/state where the property is located
        
    Returns:
        Dictionary with breakdown of costs
    """
    # Regional property transfer tax rates
    transfer_tax_rates = {
        "berlin": 0.06,
        "hamburg": 0.045,
        "bayern": 0.035,
        "brandenburg": 0.065,
        # Add more regions as needed
    }
    
    # Get transfer tax rate for the region, default to 5%
    transfer_tax_rate = transfer_tax_rates.get(region.lower(), 0.05)
    
    # Calculate costs
    transfer_tax = purchase_price * transfer_tax_rate
    notary_fee = purchase_price * 0.015  # Typically 1.5% of purchase price
    land_registry = purchase_price * 0.005  # Typically 0.5% of purchase price
    agent_fee = purchase_price * 0.0357  # Typically 3.57% (including VAT)
    
    # Total closing costs
    closing_costs = transfer_tax + notary_fee + land_registry + agent_fee
    
    # Total acquisition cost
    total_cost = purchase_price + closing_costs
    
    return {
        "purchase_price": purchase_price,
        "transfer_tax": transfer_tax,
        "notary_fee": notary_fee,
        "land_registry": land_registry,
        "agent_fee": agent_fee,
        "closing_costs": closing_costs,
        "total_acquisition_cost": total_cost
    }


def calculate_financing(purchase_price: float, 
                        closing_costs: float,
                        available_cash: float,
                        down_payment_percentage: Optional[float] = None) -> Dict[str, float]:
    """
    Calculate financing details based on available cash and down payment percentage
    
    Args:
        purchase_price: The purchase price of the property
        closing_costs: Total closing costs
        available_cash: Available cash for investment
        down_payment_percentage: Desired down payment as percentage of purchase price (optional)
        
    Returns:
        Dictionary with financing details
    """
    total_cost = purchase_price + closing_costs
    
    # If down payment percentage is specified, calculate required cash
    if down_payment_percentage is not None:
        down_payment = purchase_price * (down_payment_percentage / 100)
        required_cash = down_payment + closing_costs
        cash_shortage = max(0, required_cash - available_cash)
        loan_amount = purchase_price - down_payment + cash_shortage
    # Otherwise, calculate based on available cash
    else:
        # Available cash after closing costs
        cash_after_closing = available_cash - closing_costs
        
        # If there's not enough cash for closing costs
        if cash_after_closing < 0:
            down_payment = 0
            loan_amount = total_cost
            cash_shortage = abs(cash_after_closing)
        else:
            down_payment = cash_after_closing
            loan_amount = purchase_price - down_payment
            cash_shortage = 0
        
        down_payment_percentage = (down_payment / purchase_price) * 100 if purchase_price > 0 else 0
    
    # Check if down payment meets minimum requirements (typically 20%)
    meets_min_requirement = down_payment_percentage >= 20
    
    return {
        "available_cash": available_cash,
        "down_payment": down_payment,
        "down_payment_percentage": down_payment_percentage,
        "loan_amount": loan_amount,
        "cash_shortage": cash_shortage,
        "meets_min_requirement": meets_min_requirement
    }


def calculate_mortgage_payment(loan_amount: float, 
                              interest_rate: float,
                              repayment_rate: float,
                              term_years: int) -> Dict[str, Any]:
    """
    Calculate mortgage payment and amortization schedule
    
    Args:
        loan_amount: Amount of the loan
        interest_rate: Annual interest rate in percentage (e.g., 3.5)
        repayment_rate: Annual repayment rate in percentage (Tilgung)
        term_years: Term of the loan in years
        
    Returns:
        Dictionary with payment details and amortization schedule
    """
    if loan_amount <= 0 or interest_rate <= 0 or repayment_rate <= 0 or term_years <= 0:
        return {
            "error": "Invalid input parameters",
            "success": False
        }
    
    # Convert percentages to decimal
    interest_rate_decimal = interest_rate / 100
    repayment_rate_decimal = repayment_rate / 100
    
    # Annual and monthly payment rates
    annual_rate = interest_rate_decimal + repayment_rate_decimal
    monthly_rate = annual_rate / 12
    
    # Monthly payment
    monthly_payment = loan_amount * monthly_rate
    
    # Initial values for amortization schedule
    remaining_balance = loan_amount
    interest_portion = loan_amount * interest_rate_decimal / 12
    principal_portion = monthly_payment - interest_portion
    
    # Generate amortization schedule
    schedule = []
    yearly_schedule = []
    
    for year in range(1, term_years + 1):
        yearly_interest = 0
        yearly_principal = 0
        
        for month in range(1, 13):
            # Calculate interest and principal for this payment
            interest_portion = remaining_balance * interest_rate_decimal / 12
            principal_portion = monthly_payment - interest_portion
            
            # Update remaining balance
            remaining_balance -= principal_portion
            
            # Add to yearly totals
            yearly_interest += interest_portion
            yearly_principal += principal_portion
            
            # Add to detailed schedule if needed
            # schedule.append({
            #     "year": year,
            #     "month": month,
            #     "payment": monthly_payment,
            #     "interest": interest_portion,
            #     "principal": principal_portion,
            #     "remaining_balance": remaining_balance
            # })
        
        # Add yearly summary
        yearly_schedule.append({
            "year": year,
            "payment": monthly_payment * 12,
            "interest": yearly_interest,
            "principal": yearly_principal,
            "remaining_balance": remaining_balance
        })
    
    return {
        "loan_amount": loan_amount,
        "interest_rate": interest_rate,
        "repayment_rate": repayment_rate,
        "term_years": term_years,
        "monthly_payment": monthly_payment,
        "annual_payment": monthly_payment * 12,
        "total_payments": monthly_payment * 12 * term_years,
        "total_interest": sum(year["interest"] for year in yearly_schedule),
        "amortization_schedule": yearly_schedule,
        "success": True
    }


def calculate_rental_income(units: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate rental income from multiple units
    
    Args:
        units: List of rental units with current/potential rent
        
    Returns:
        Dictionary with income details
    """
    # Current rental income
    current_rent = sum(unit.get("current_rent", 0) for unit in units if unit.get("is_occupied", False))
    
    # Potential rental income (if all units were rented at their potential rent)
    potential_rent = sum(
        unit.get("current_rent", 0) if unit.get("is_occupied", False) else unit.get("potential_rent", 0)
        for unit in units
    )
    
    # Vacancy loss (assuming 5% vacancy rate)
    vacancy_rate = 0.05
    vacancy_loss = potential_rent * vacancy_rate
    
    # Effective rental income
    effective_rent = potential_rent - vacancy_loss
    
    return {
        "current_monthly_rent": current_rent,
        "current_annual_rent": current_rent * 12,
        "potential_monthly_rent": potential_rent,
        "potential_annual_rent": potential_rent * 12,
        "vacancy_rate": vacancy_rate,
        "vacancy_loss_monthly": vacancy_loss,
        "vacancy_loss_annual": vacancy_loss * 12,
        "effective_monthly_rent": effective_rent,
        "effective_annual_rent": effective_rent * 12
    }


def calculate_operating_expenses(gross_annual_income: float, 
                                property_tax: float,
                                insurance: float,
                                maintenance_percentage: float = 10.0,
                                management_percentage: float = 5.0,
                                reserve_percentage: float = 3.0,
                                additional_expenses: List[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Calculate operating expenses
    
    Args:
        gross_annual_income: Gross annual rental income
        property_tax: Annual property tax
        insurance: Annual insurance cost
        maintenance_percentage: Maintenance cost as percentage of gross income
        management_percentage: Property management cost as percentage of gross income
        reserve_percentage: Reserve fund as percentage of gross income
        additional_expenses: List of additional expenses
        
    Returns:
        Dictionary with expense details
    """
    # Calculate expenses based on percentages
    maintenance = gross_annual_income * (maintenance_percentage / 100)
    management = gross_annual_income * (management_percentage / 100)
    reserve = gross_annual_income * (reserve_percentage / 100)
    
    # Additional expenses
    additional = 0
    if additional_expenses:
        additional = sum(expense.get("amount", 0) for expense in additional_expenses)
    
    # Total operating expenses
    total_expenses = property_tax + insurance + maintenance + management + reserve + additional
    
    # Expense ratio
    expense_ratio = total_expenses / gross_annual_income if gross_annual_income > 0 else 0
    
    return {
        "property_tax_annual": property_tax,
        "insurance_annual": insurance,
        "maintenance_annual": maintenance,
        "management_annual": management,
        "reserve_annual": reserve,
        "additional_annual": additional,
        "total_annual_expenses": total_expenses,
        "total_monthly_expenses": total_expenses / 12,
        "expense_ratio": expense_ratio
    }


def calculate_tax_benefits(building_value: float, 
                          loan_amount: float,
                          interest_rate: float,
                          marginal_tax_rate: float,
                          property_age_years: int,
                          annual_operating_expenses: float = 0,
                          additional_werbungskosten: float = 0,
                          use_progressive_tax: bool = False,
                          other_income: float = 0) -> Dict[str, Any]:
    """
    Calculate tax benefits from property investment according to German tax regulations
    
    Args:
        building_value: Value of the building (excluding land)
        loan_amount: Amount of the loan
        interest_rate: Annual interest rate in percentage
        marginal_tax_rate: Investor's marginal tax rate in percentage
        property_age_years: Age of the property in years
        annual_operating_expenses: Annual operating expenses that can be tax-deductible
        additional_werbungskosten: Additional income-related expenses beyond standard allowance
        use_progressive_tax: Whether to use progressive tax calculation instead of flat rate
        other_income: Other taxable income (relevant if use_progressive_tax is True)
        
    Returns:
        Dictionary with tax benefit details and visualization data
    """
    # Convert percentages to decimal
    interest_rate_decimal = interest_rate / 100
    marginal_tax_rate_decimal = marginal_tax_rate / 100
    
    # Calculate depreciation rate based on property age and German regulations
    # Standard rate for residential buildings is typically 2% per year (50 years linear depreciation)
    depreciation_rate = 0.02  # 2% per year
    
    # For buildings older than 2007, different rates may apply
    if property_age_years > 18:  # Built before 2007 (as of 2025)
        depreciation_rate = 0.025  # 2.5% per year
    
    # For historical buildings, even higher rates may apply under certain conditions
    is_historical_building = False  # This would need to be passed as a parameter in a future enhancement
    if is_historical_building:
        depreciation_rate = 0.04  # 4% per year for historical buildings
    
    # Annual depreciation (AfA - Absetzung für Abnutzung)
    annual_depreciation = building_value * depreciation_rate
    
    # Annual interest expense (Schuldzinsen)
    annual_interest = loan_amount * interest_rate_decimal
    
    # Standard Werbungskosten allowance for income from renting (Pauschale)
    standard_werbungskosten = 1000  # As of 2023/2024
    
    # Calculate total Werbungskosten
    # Operating expenses are considered Werbungskosten in German tax law
    total_werbungskosten = max(standard_werbungskosten, annual_operating_expenses + additional_werbungskosten)
    
    # Werbungskosten above standard allowance
    werbungskosten_above_standard = max(0, total_werbungskosten - standard_werbungskosten)
    
    # Total deductible expenses for tax purposes
    total_deductible = annual_depreciation + annual_interest + werbungskosten_above_standard
    
    # Prepare tax brackets for progressive tax calculation if needed
    tax_savings = 0
    
    if use_progressive_tax and other_income > 0:
        # Simplified German income tax brackets (2023/2024)
        def calculate_german_income_tax(income):
            # Basic tax allowance (Grundfreibetrag)
            grundfreibetrag = 11604  # for 2024
            
            if income <= grundfreibetrag:
                return 0
            
            # Zone 1: 14% to 24%
            elif income <= 17602:
                y = (income - grundfreibetrag) / 10000
                tax = (1088.67 * y + 1990) * y
                
            # Zone 2: 24% to 42%
            elif income <= 66761:
                z = (income - 17602) / 10000
                tax = (206.43 * z + 2397) * z + 869.32
                
            # Zone 3: 42%
            elif income <= 277826:
                tax = 0.42 * income - 10642.82
                
            # Zone 4: 45%
            else:
                tax = 0.45 * income - 18952.97
                
            return tax
        
        # Calculate tax with and without the property deductions
        tax_without_property = calculate_german_income_tax(other_income)
        tax_with_property = calculate_german_income_tax(max(0, other_income - total_deductible))
        
        # Tax savings is the difference
        tax_savings = tax_without_property - tax_with_property
    else:
        # Simple calculation based on marginal tax rate
        tax_savings = total_deductible * marginal_tax_rate_decimal
    
    # Generate data for visualization
    werbungskosten_data = []
    for wk in range(0, 10001, 500):
        effective_wk = max(standard_werbungskosten, annual_operating_expenses + wk)
        wk_above_standard = max(0, effective_wk - standard_werbungskosten)
        deductible = annual_depreciation + annual_interest + wk_above_standard
        tax_benefit = deductible * marginal_tax_rate_decimal
        
        werbungskosten_data.append({
            "werbungskosten": wk,
            "total_deductible": deductible,
            "tax_savings": tax_benefit
        })
    
    # Generate data for marginal tax rate visualization
    tax_rate_data = []
    for rate in range(0, 51, 5):  # 0% to 50% in 5% steps
        rate_decimal = rate / 100
        tax_benefit = total_deductible * rate_decimal
        
        tax_rate_data.append({
            "tax_rate": rate,
            "tax_savings": tax_benefit
        })
    
    return {
        "annual_depreciation": annual_depreciation,
        "annual_interest_expense": annual_interest,
        "standard_werbungskosten": standard_werbungskosten,
        "total_werbungskosten": total_werbungskosten,
        "werbungskosten_above_standard": werbungskosten_above_standard,
        "total_deductible_expenses": total_deductible,
        "annual_tax_savings": tax_savings,
        "monthly_tax_savings": tax_savings / 12,
        "effective_tax_rate": (tax_savings / total_deductible * 100) if total_deductible > 0 else 0,
        "visualization_data": {
            "werbungskosten_impact": werbungskosten_data,
            "tax_rate_impact": tax_rate_data
        }
    }


def calculate_cash_flow(rental_income: Dict[str, float],
                       operating_expenses: Dict[str, float],
                       mortgage_payment: Dict[str, float],
                       tax_benefits: Dict[str, float] = None) -> Dict[str, float]:
    """
    Calculate cash flow from property investment
    
    Args:
        rental_income: Rental income dictionary
        operating_expenses: Operating expenses dictionary
        mortgage_payment: Mortgage payment dictionary
        tax_benefits: Tax benefits dictionary (optional)
        
    Returns:
        Dictionary with cash flow details
    """
    # Monthly and annual effective rental income
    monthly_income = rental_income.get("effective_monthly_rent", 0)
    annual_income = rental_income.get("effective_annual_rent", 0)
    
    # Monthly and annual operating expenses
    monthly_expenses = operating_expenses.get("total_monthly_expenses", 0)
    annual_expenses = operating_expenses.get("total_annual_expenses", 0)
    
    # Monthly and annual mortgage payment
    monthly_mortgage = mortgage_payment.get("monthly_payment", 0)
    annual_mortgage = mortgage_payment.get("annual_payment", 0)
    
    # Net operating income (NOI)
    monthly_noi = monthly_income - monthly_expenses
    annual_noi = annual_income - annual_expenses
    
    # Cash flow before tax benefits
    monthly_cash_flow_before_tax = monthly_noi - monthly_mortgage
    annual_cash_flow_before_tax = annual_noi - annual_mortgage
    
    # Cash flow after tax benefits
    monthly_tax_savings = tax_benefits.get("monthly_tax_savings", 0) if tax_benefits else 0
    annual_tax_savings = tax_benefits.get("annual_tax_savings", 0) if tax_benefits else 0
    
    monthly_cash_flow_after_tax = monthly_cash_flow_before_tax + monthly_tax_savings
    annual_cash_flow_after_tax = annual_cash_flow_before_tax + annual_tax_savings
    
    return {
        "monthly_income": monthly_income,
        "annual_income": annual_income,
        "monthly_expenses": monthly_expenses,
        "annual_expenses": annual_expenses,
        "monthly_mortgage": monthly_mortgage,
        "annual_mortgage": annual_mortgage,
        "monthly_noi": monthly_noi,
        "annual_noi": annual_noi,
        "monthly_cash_flow_before_tax": monthly_cash_flow_before_tax,
        "annual_cash_flow_before_tax": annual_cash_flow_before_tax,
        "monthly_tax_savings": monthly_tax_savings,
        "annual_tax_savings": annual_tax_savings,
        "monthly_cash_flow_after_tax": monthly_cash_flow_after_tax,
        "annual_cash_flow_after_tax": annual_cash_flow_after_tax
    }


def calculate_investment_metrics(purchase_price: float,
                               closing_costs: float,
                               down_payment: float,
                               annual_noi: float,
                               annual_cash_flow: float) -> Dict[str, float]:
    """
    Calculate investment metrics such as cap rate, cash-on-cash return, and ROI
    
    Args:
        purchase_price: Purchase price of the property
        closing_costs: Closing costs
        down_payment: Down payment amount
        annual_noi: Annual net operating income
        annual_cash_flow: Annual cash flow after tax
        
    Returns:
        Dictionary with investment metrics
    """
    # Total investment
    total_investment = purchase_price + closing_costs
    total_cash_invested = down_payment + closing_costs
    
    # Cap rate = NOI / Total Investment
    cap_rate = annual_noi / total_investment if total_investment > 0 else 0
    
    # Cash-on-cash return = Annual Cash Flow / Total Cash Invested
    cash_on_cash = annual_cash_flow / total_cash_invested if total_cash_invested > 0 else 0
    
    # ROI (simplified, not accounting for appreciation)
    roi = cash_on_cash  # In this simplified model, ROI equals cash-on-cash return
    
    return {
        "total_investment": total_investment,
        "total_cash_invested": total_cash_invested,
        "cap_rate": cap_rate,
        "cap_rate_percentage": cap_rate * 100,
        "cash_on_cash_return": cash_on_cash,
        "cash_on_cash_percentage": cash_on_cash * 100,
        "roi": roi,
        "roi_percentage": roi * 100
    }


def analyze_property_investment(property_data: Dict[str, Any],
                              units_data: List[Dict[str, Any]],
                              financing_data: Dict[str, Any],
                              expenses_data: Dict[str, Any],
                              tax_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a comprehensive analysis of a property investment
    
    Args:
        property_data: Property details
        units_data: Rental units details
        financing_data: Financing details
        expenses_data: Operating expenses details
        tax_data: Tax-related details
        
    Returns:
        Dictionary with comprehensive analysis results
    """
    # Calculate acquisition costs
    acquisition = calculate_total_acquisition_cost(
        property_data.get("purchase_price", 0),
        property_data.get("region", "berlin")
    )
    
    # Calculate financing
    financing = calculate_financing(
        acquisition.get("purchase_price", 0),
        acquisition.get("closing_costs", 0),
        financing_data.get("available_cash", 0),
        financing_data.get("down_payment_percentage")
    )
    
    # Calculate mortgage payment
    mortgage = calculate_mortgage_payment(
        financing.get("loan_amount", 0),
        financing_data.get("interest_rate", 0),
        financing_data.get("repayment_rate", 0),
        financing_data.get("term_years", 30)
    )
    
    # Calculate rental income
    income = calculate_rental_income(units_data)
    
    # Calculate operating expenses
    expenses = calculate_operating_expenses(
        income.get("effective_annual_rent", 0),
        expenses_data.get("property_tax", 0),
        expenses_data.get("insurance", 0),
        expenses_data.get("maintenance_percentage", 10.0),
        expenses_data.get("management_percentage", 5.0),
        expenses_data.get("reserve_percentage", 3.0),
        expenses_data.get("additional_expenses")
    )
    
    # Calculate tax benefits
    tax_benefits = calculate_tax_benefits(
        tax_data.get("building_value", 0),
        financing.get("loan_amount", 0),
        financing_data.get("interest_rate", 0),
        tax_data.get("marginal_tax_rate", 0),
        property_data.get("property_age_years", 0)
    )
    
    # Calculate cash flow
    cash_flow = calculate_cash_flow(
        income,
        expenses,
        mortgage,
        tax_benefits
    )
    
    # Calculate investment metrics
    metrics = calculate_investment_metrics(
        acquisition.get("purchase_price", 0),
        acquisition.get("closing_costs", 0),
        financing.get("down_payment", 0),
        cash_flow.get("annual_noi", 0),
        cash_flow.get("annual_cash_flow_after_tax", 0)
    )
    
    # Return comprehensive analysis
    return {
        "acquisition": acquisition,
        "financing": financing,
        "mortgage": mortgage,
        "income": income,
        "expenses": expenses,
        "tax_benefits": tax_benefits,
        "cash_flow": cash_flow,
        "metrics": metrics,
        "analysis_summary": {
            "monthly_cash_flow": cash_flow.get("monthly_cash_flow_after_tax", 0),
            "annual_cash_flow": cash_flow.get("annual_cash_flow_after_tax", 0),
            "cap_rate": metrics.get("cap_rate_percentage", 0),
            "cash_on_cash": metrics.get("cash_on_cash_percentage", 0),
            "roi": metrics.get("roi_percentage", 0)
        }
    }