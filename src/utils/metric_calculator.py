"""
Real-time calculation engine for property investment metrics
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List, Set, Callable
from datetime import datetime
import copy
import json

from ..utils.sse_updates import send_update

logger = logging.getLogger(__name__)

class MetricCalculator:
    """
    Calculation engine for real-time property investment metrics
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(MetricCalculator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the metric calculator"""
        if self._initialized:
            return
            
        # Store calculation cache by scenario_id
        self._cache = {}
        # Store calculation tasks
        self._tasks = {}
        self._initialized = True
        logger.info("MetricCalculator initialized")
    
    def calculate_metrics(self, scenario_id: int, input_data: Dict[str, Any], 
                           send_updates: bool = True) -> Dict[str, Any]:
        """
        Calculate investment metrics based on input data
        
        Args:
            scenario_id (int): Scenario ID
            input_data (Dict[str, Any]): Input data for calculations
            send_updates (bool, optional): Whether to send real-time updates. Defaults to True.
            
        Returns:
            Dict[str, Any]: Calculated metrics
        """
        # Check if we already have a cache for this scenario
        if scenario_id not in self._cache:
            self._cache[scenario_id] = {
                "input_data": {},
                "intermediate_results": {},
                "results": {}
            }
        
        # Update input data in cache
        self._cache[scenario_id]["input_data"].update(input_data)
        
        # Calculate metrics
        results = self._perform_calculations(scenario_id, send_updates)
        
        # Store results in cache
        self._cache[scenario_id]["results"] = results
        
        return results
    
    async def calculate_metrics_async(self, scenario_id: int, input_data: Dict[str, Any],
                                     send_updates: bool = True) -> Dict[str, Any]:
        """
        Calculate investment metrics asynchronously
        
        Args:
            scenario_id (int): Scenario ID
            input_data (Dict[str, Any]): Input data for calculations
            send_updates (bool, optional): Whether to send real-time updates. Defaults to True.
            
        Returns:
            Dict[str, Any]: Calculated metrics
        """
        # Check if we already have a task for this scenario
        if scenario_id in self._tasks and not self._tasks[scenario_id].done():
            # Cancel existing task
            self._tasks[scenario_id].cancel()
            try:
                await self._tasks[scenario_id]
            except asyncio.CancelledError:
                logger.info(f"Cancelled existing calculation task for scenario {scenario_id}")
        
        # Create new task
        self._tasks[scenario_id] = asyncio.create_task(
            self._calculate_metrics_async_task(scenario_id, input_data, send_updates)
        )
        
        # Wait for task to complete
        try:
            results = await self._tasks[scenario_id]
            return results
        except Exception as e:
            logger.error(f"Error in calculation task for scenario {scenario_id}: {str(e)}")
            # Return partial results if available
            if scenario_id in self._cache and "results" in self._cache[scenario_id]:
                return self._cache[scenario_id]["results"]
            return {}
    
    async def _calculate_metrics_async_task(self, scenario_id: int, input_data: Dict[str, Any],
                                           send_updates: bool = True) -> Dict[str, Any]:
        """
        Asynchronous task for calculating metrics
        
        Args:
            scenario_id (int): Scenario ID
            input_data (Dict[str, Any]): Input data for calculations
            send_updates (bool, optional): Whether to send real-time updates. Defaults to True.
            
        Returns:
            Dict[str, Any]: Calculated metrics
        """
        # Check if we already have a cache for this scenario
        if scenario_id not in self._cache:
            self._cache[scenario_id] = {
                "input_data": {},
                "intermediate_results": {},
                "results": {}
            }
        
        # Update input data in cache
        self._cache[scenario_id]["input_data"].update(input_data)
        
        # Calculate metrics with async-aware code
        results = {}
        
        # Property information
        property_data = self._cache[scenario_id]["input_data"].get("property", {})
        purchase_price = property_data.get("purchase_price", 0)
        
        # Calculate property acquisition costs
        acquisition_costs = self._calculate_acquisition_costs(scenario_id, property_data)
        results["acquisition_costs"] = acquisition_costs
        
        if send_updates:
            # Send update for acquisition costs
            send_update(scenario_id, "metric_update", {
                "acquisition_costs": acquisition_costs
            })
            # Simulate some processing time
            await asyncio.sleep(0.1)
        
        # Financing information
        financing_data = self._cache[scenario_id]["input_data"].get("financing", {})
        
        # Calculate financing metrics
        financing_metrics = self._calculate_financing_metrics(scenario_id, financing_data, purchase_price)
        results.update(financing_metrics)
        
        if send_updates:
            # Send update for financing metrics
            send_update(scenario_id, "metric_update", financing_metrics)
            await asyncio.sleep(0.1)
        
        # Rental information
        rental_data = self._cache[scenario_id]["input_data"].get("rental", {})
        
        # Calculate rental income metrics
        rental_metrics = self._calculate_rental_metrics(scenario_id, rental_data)
        results.update(rental_metrics)
        
        if send_updates:
            # Send update for rental metrics
            send_update(scenario_id, "metric_update", rental_metrics)
            await asyncio.sleep(0.1)
        
        # Expense information
        expense_data = self._cache[scenario_id]["input_data"].get("expenses", {})
        
        # Calculate expense metrics
        expense_metrics = self._calculate_expense_metrics(scenario_id, expense_data, rental_metrics.get("annual_rental_income", 0))
        results.update(expense_metrics)
        
        if send_updates:
            # Send update for expense metrics
            send_update(scenario_id, "metric_update", expense_metrics)
            await asyncio.sleep(0.1)
        
        # Calculate cash flow metrics
        cash_flow_metrics = self._calculate_cash_flow_metrics(
            scenario_id, 
            rental_metrics.get("annual_rental_income", 0),
            financing_metrics.get("annual_mortgage_payment", 0),
            expense_metrics.get("annual_expenses", 0)
        )
        results.update(cash_flow_metrics)
        
        if send_updates:
            # Send update for cash flow metrics
            send_update(scenario_id, "metric_update", cash_flow_metrics)
            await asyncio.sleep(0.1)
        
        # Calculate investment metrics
        investment_metrics = self._calculate_investment_metrics(
            scenario_id,
            cash_flow_metrics.get("annual_cash_flow", 0),
            acquisition_costs.get("total_acquisition_cost", 0),
            purchase_price
        )
        results.update(investment_metrics)
        
        if send_updates:
            # Send update for investment metrics
            send_update(scenario_id, "metric_update", investment_metrics)
            await asyncio.sleep(0.1)
        
        # Store results in cache
        self._cache[scenario_id]["results"] = results
        
        # Send final update
        if send_updates:
            send_update(scenario_id, "calculation_complete", {
                "status": "complete",
                "scenario_id": scenario_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return results
    
    def _perform_calculations(self, scenario_id: int, send_updates: bool = True) -> Dict[str, Any]:
        """
        Perform all calculations for a scenario
        
        Args:
            scenario_id (int): Scenario ID
            send_updates (bool, optional): Whether to send real-time updates. Defaults to True.
            
        Returns:
            Dict[str, Any]: Calculated metrics
        """
        results = {}
        
        # Property information
        property_data = self._cache[scenario_id]["input_data"].get("property", {})
        purchase_price = property_data.get("purchase_price", 0)
        
        # Calculate property acquisition costs
        acquisition_costs = self._calculate_acquisition_costs(scenario_id, property_data)
        results["acquisition_costs"] = acquisition_costs
        
        if send_updates:
            # Send update for acquisition costs
            send_update(scenario_id, "metric_update", {
                "acquisition_costs": acquisition_costs
            })
        
        # Financing information
        financing_data = self._cache[scenario_id]["input_data"].get("financing", {})
        
        # Calculate financing metrics
        financing_metrics = self._calculate_financing_metrics(scenario_id, financing_data, purchase_price)
        results.update(financing_metrics)
        
        if send_updates:
            # Send update for financing metrics
            send_update(scenario_id, "metric_update", financing_metrics)
        
        # Rental information
        rental_data = self._cache[scenario_id]["input_data"].get("rental", {})
        
        # Calculate rental income metrics
        rental_metrics = self._calculate_rental_metrics(scenario_id, rental_data)
        results.update(rental_metrics)
        
        if send_updates:
            # Send update for rental metrics
            send_update(scenario_id, "metric_update", rental_metrics)
        
        # Expense information
        expense_data = self._cache[scenario_id]["input_data"].get("expenses", {})
        
        # Calculate expense metrics
        expense_metrics = self._calculate_expense_metrics(scenario_id, expense_data, rental_metrics.get("annual_rental_income", 0))
        results.update(expense_metrics)
        
        if send_updates:
            # Send update for expense metrics
            send_update(scenario_id, "metric_update", expense_metrics)
        
        # Calculate cash flow metrics
        cash_flow_metrics = self._calculate_cash_flow_metrics(
            scenario_id, 
            rental_metrics.get("annual_rental_income", 0),
            financing_metrics.get("annual_mortgage_payment", 0),
            expense_metrics.get("annual_expenses", 0)
        )
        results.update(cash_flow_metrics)
        
        if send_updates:
            # Send update for cash flow metrics
            send_update(scenario_id, "metric_update", cash_flow_metrics)
        
        # Calculate investment metrics
        investment_metrics = self._calculate_investment_metrics(
            scenario_id,
            cash_flow_metrics.get("annual_cash_flow", 0),
            acquisition_costs.get("total_acquisition_cost", 0),
            purchase_price
        )
        results.update(investment_metrics)
        
        if send_updates:
            # Send update for investment metrics
            send_update(scenario_id, "metric_update", investment_metrics)
            
            # Send final update
            send_update(scenario_id, "calculation_complete", {
                "status": "complete",
                "scenario_id": scenario_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return results
    
    def _calculate_acquisition_costs(self, scenario_id: int, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate property acquisition costs
        
        Args:
            scenario_id (int): Scenario ID
            property_data (Dict[str, Any]): Property data
            
        Returns:
            Dict[str, Any]: Acquisition costs
        """
        purchase_price = property_data.get("purchase_price", 0)
        region = property_data.get("region", "berlin")
        
        # Calculate costs based on region
        if region.lower() == "berlin":
            # Berlin rates
            notary_pct = 1.5
            land_transfer_tax_pct = 6.0  # Berlin has higher transfer tax
            agent_fee_pct = 7.14  # Standard is 7.14% (6% + 19% VAT)
        else:
            # Default German rates
            notary_pct = 1.5
            land_transfer_tax_pct = 5.0  # Most common rate
            agent_fee_pct = 7.14  # Standard is 7.14% (6% + 19% VAT)
        
        # Override with scenario-specific rates if provided
        override_data = self._cache[scenario_id]["input_data"].get("acquisition_costs_override", {})
        notary_pct = override_data.get("notary_pct", notary_pct)
        land_transfer_tax_pct = override_data.get("land_transfer_tax_pct", land_transfer_tax_pct)
        agent_fee_pct = override_data.get("agent_fee_pct", agent_fee_pct)
        
        # Calculate costs
        notary_fee = purchase_price * (notary_pct / 100)
        land_transfer_tax = purchase_price * (land_transfer_tax_pct / 100)
        agent_fee = purchase_price * (agent_fee_pct / 100)
        
        # Additional costs if provided
        additional_costs = override_data.get("additional_costs", 0)
        
        # Total acquisition cost
        total_acquisition_cost = purchase_price + notary_fee + land_transfer_tax + agent_fee + additional_costs
        
        # Return results
        return {
            "purchase_price": purchase_price,
            "notary_fee": notary_fee,
            "land_transfer_tax": land_transfer_tax,
            "agent_fee": agent_fee,
            "additional_costs": additional_costs,
            "total_acquisition_cost": total_acquisition_cost
        }
    
    def _calculate_financing_metrics(self, scenario_id: int, financing_data: Dict[str, Any], 
                                    purchase_price: float) -> Dict[str, Any]:
        """
        Calculate financing metrics
        
        Args:
            scenario_id (int): Scenario ID
            financing_data (Dict[str, Any]): Financing data
            purchase_price (float): Property purchase price
            
        Returns:
            Dict[str, Any]: Financing metrics
        """
        # Get financing data
        loan_amount = financing_data.get("loan_amount", 0)
        interest_rate = financing_data.get("interest_rate", 0)  # Annual interest rate in %
        repayment_rate = financing_data.get("repayment_rate", 0)  # Annual repayment in %
        term_years = financing_data.get("term_years", 30)
        
        # Calculate down payment
        down_payment = financing_data.get("down_payment", purchase_price - loan_amount)
        down_payment_percentage = (down_payment / purchase_price * 100) if purchase_price > 0 else 0
        
        # Calculate monthly payment (interest + repayment)
        annual_rate = (interest_rate + repayment_rate) / 100
        monthly_payment = (loan_amount * annual_rate) / 12 if annual_rate > 0 else 0
        
        # Annual payment
        annual_mortgage_payment = monthly_payment * 12
        
        # Calculate principal and interest portions
        monthly_interest = (loan_amount * (interest_rate / 100)) / 12
        monthly_principal = monthly_payment - monthly_interest
        
        # Calculate loan-to-value ratio
        ltv_ratio = (loan_amount / purchase_price) * 100 if purchase_price > 0 else 0
        
        # Return results
        return {
            "loan_amount": loan_amount,
            "down_payment": down_payment,
            "down_payment_percentage": down_payment_percentage,
            "interest_rate": interest_rate,
            "repayment_rate": repayment_rate,
            "term_years": term_years,
            "monthly_payment": monthly_payment,
            "annual_mortgage_payment": annual_mortgage_payment,
            "monthly_interest": monthly_interest,
            "monthly_principal": monthly_principal,
            "ltv_ratio": ltv_ratio
        }
    
    def _calculate_rental_metrics(self, scenario_id: int, rental_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate rental income metrics
        
        Args:
            scenario_id (int): Scenario ID
            rental_data (Dict[str, Any]): Rental data
            
        Returns:
            Dict[str, Any]: Rental metrics
        """
        # Get rental units
        rental_units = rental_data.get("units", [])
        
        # Calculate total monthly rental income
        monthly_rental_income = 0
        for unit in rental_units:
            # If unit is occupied, use current rent, otherwise use potential rent
            if unit.get("is_occupied", False):
                monthly_rental_income += unit.get("current_rent", 0)
            else:
                monthly_rental_income += unit.get("potential_rent", 0)
        
        # Annual rental income
        annual_rental_income = monthly_rental_income * 12
        
        # Calculate vacancy rate and loss
        vacancy_rate = rental_data.get("vacancy_rate", 5)  # Default 5%
        vacancy_loss = annual_rental_income * (vacancy_rate / 100)
        
        # Effective rental income after vacancy loss
        effective_annual_rental_income = annual_rental_income - vacancy_loss
        effective_monthly_rental_income = effective_annual_rental_income / 12
        
        # Return results
        return {
            "monthly_rental_income": monthly_rental_income,
            "annual_rental_income": annual_rental_income,
            "vacancy_rate": vacancy_rate,
            "vacancy_loss": vacancy_loss,
            "effective_annual_rental_income": effective_annual_rental_income,
            "effective_monthly_rental_income": effective_monthly_rental_income
        }
    
    def _calculate_expense_metrics(self, scenario_id: int, expense_data: Dict[str, Any],
                                  annual_rental_income: float) -> Dict[str, Any]:
        """
        Calculate expense metrics
        
        Args:
            scenario_id (int): Scenario ID
            expense_data (Dict[str, Any]): Expense data
            annual_rental_income (float): Annual rental income
            
        Returns:
            Dict[str, Any]: Expense metrics
        """
        # Get expense items
        expense_items = expense_data.get("items", [])
        
        # Initialize expense categories
        fixed_expenses = 0
        variable_expenses = 0
        
        # Process each expense item
        for item in expense_items:
            amount = item.get("amount", 0)
            frequency = item.get("frequency", "annual")
            is_percentage = item.get("is_percentage", False)
            
            # Convert to annual amount
            if frequency == "monthly":
                annual_amount = amount * 12
            elif frequency == "quarterly":
                annual_amount = amount * 4
            else:  # annual
                annual_amount = amount
            
            # Handle percentage-based amounts
            if is_percentage:
                annual_amount = annual_rental_income * (amount / 100)
            
            # Add to appropriate category
            if item.get("is_fixed", True):
                fixed_expenses += annual_amount
            else:
                variable_expenses += annual_amount
        
        # Total annual expenses
        annual_expenses = fixed_expenses + variable_expenses
        
        # Monthly expenses
        monthly_expenses = annual_expenses / 12
        
        # Expense ratio
        expense_ratio = (annual_expenses / annual_rental_income * 100) if annual_rental_income > 0 else 0
        
        # Return results
        return {
            "annual_fixed_expenses": fixed_expenses,
            "annual_variable_expenses": variable_expenses,
            "annual_expenses": annual_expenses,
            "monthly_expenses": monthly_expenses,
            "expense_ratio": expense_ratio
        }
    
    def _calculate_cash_flow_metrics(self, scenario_id: int, annual_rental_income: float,
                                   annual_mortgage_payment: float, annual_expenses: float) -> Dict[str, Any]:
        """
        Calculate cash flow metrics
        
        Args:
            scenario_id (int): Scenario ID
            annual_rental_income (float): Annual rental income
            annual_mortgage_payment (float): Annual mortgage payment
            annual_expenses (float): Annual expenses
            
        Returns:
            Dict[str, Any]: Cash flow metrics
        """
        # Net operating income (NOI)
        noi = annual_rental_income - annual_expenses
        
        # Annual cash flow
        annual_cash_flow = noi - annual_mortgage_payment
        
        # Monthly cash flow
        monthly_cash_flow = annual_cash_flow / 12
        
        # Debt service coverage ratio (DSCR)
        dscr = noi / annual_mortgage_payment if annual_mortgage_payment > 0 else float('inf')
        
        # Return results
        return {
            "net_operating_income": noi,
            "annual_cash_flow": annual_cash_flow,
            "monthly_cash_flow": monthly_cash_flow,
            "debt_service_coverage_ratio": dscr
        }
    
    def _calculate_investment_metrics(self, scenario_id: int, annual_cash_flow: float,
                                    total_acquisition_cost: float, purchase_price: float) -> Dict[str, Any]:
        """
        Calculate investment metrics
        
        Args:
            scenario_id (int): Scenario ID
            annual_cash_flow (float): Annual cash flow
            total_acquisition_cost (float): Total acquisition cost
            purchase_price (float): Property purchase price
            
        Returns:
            Dict[str, Any]: Investment metrics
        """
        # Get investment data
        investment_data = self._cache[scenario_id]["input_data"].get("investment", {})
        
        # Down payment
        down_payment = investment_data.get("down_payment", 0)
        if down_payment == 0:
            # Try to get from financing data
            financing_data = self._cache[scenario_id]["input_data"].get("financing", {})
            down_payment = financing_data.get("down_payment", 0)
        
        # Cash invested (down payment + closing costs)
        cash_invested = investment_data.get("cash_invested", down_payment + (total_acquisition_cost - purchase_price))
        
        # Cash on cash return
        cash_on_cash_return = (annual_cash_flow / cash_invested * 100) if cash_invested > 0 else 0
        
        # Capitalization rate (Cap Rate)
        noi = self._cache[scenario_id]["intermediate_results"].get("noi", 0)
        if noi == 0:
            # Try to calculate from other data
            annual_rental_income = self._cache[scenario_id]["results"].get("annual_rental_income", 0)
            annual_expenses = self._cache[scenario_id]["results"].get("annual_expenses", 0)
            noi = annual_rental_income - annual_expenses
        
        cap_rate = (noi / purchase_price * 100) if purchase_price > 0 else 0
        
        # Return on investment (ROI)
        # For simplicity, using a basic calculation
        # In a real implementation, this would include appreciation, tax benefits, etc.
        roi = cash_on_cash_return  # Simplification for now
        
        # Gross rent multiplier (GRM)
        annual_rental_income = self._cache[scenario_id]["results"].get("annual_rental_income", 0)
        grm = purchase_price / annual_rental_income if annual_rental_income > 0 else 0
        
        # Price per square meter
        property_data = self._cache[scenario_id]["input_data"].get("property", {})
        size_sqm = property_data.get("size_sqm", 0)
        price_per_sqm = purchase_price / size_sqm if size_sqm > 0 else 0
        
        # Return results
        return {
            "cash_invested": cash_invested,
            "cash_on_cash_return": cash_on_cash_return,
            "cap_rate": cap_rate,
            "roi": roi,
            "gross_rent_multiplier": grm,
            "price_per_sqm": price_per_sqm
        }
    
    def clear_cache(self, scenario_id: Optional[int] = None) -> None:
        """
        Clear calculation cache
        
        Args:
            scenario_id (int, optional): Scenario ID to clear cache for.
                If None, all caches will be cleared.
        """
        if scenario_id is None:
            # Clear all caches
            self._cache = {}
            logger.info("Cleared all calculation caches")
        elif scenario_id in self._cache:
            # Clear cache for specific scenario
            self._cache[scenario_id] = {
                "input_data": {},
                "intermediate_results": {},
                "results": {}
            }
            logger.info(f"Cleared calculation cache for scenario {scenario_id}")

# Create global singleton instance
metric_calculator = MetricCalculator()