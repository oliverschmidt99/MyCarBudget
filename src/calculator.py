# src/calculator.py
from .car import Car
from .financing import Financing
from .insurance import Insurance
import math

class CostCalculator:
    def __init__(self,
                 car: Car,
                 financing: Financing,
                 insurance: Insurance,
                 km_per_year: float,
                 fuel_price_per_liter: float,
                 operating_cost_increase_percent: float):
        self.car = car
        self.financing = financing
        self.insurance = insurance
        self.km_per_year = km_per_year
        self.fuel_price_per_liter = fuel_price_per_liter
        self.operating_cost_increase_percent = operating_cost_increase_percent
        self.km_per_month = self.km_per_year / 12.0 if self.km_per_year else 0.0

    def _calculate_monthly_loan_payment(self) -> float:
        principal = self.car.purchase_price
        annual_interest_rate_percent = self.financing.interest_rate_percent
        loan_term_years = self.financing.duration_years
        balloon_payment = self.financing.balloon_payment

        if loan_term_years <= 0 or principal < 0:
            return 0.0
        
        monthly_interest_rate = (annual_interest_rate_percent / 100.0) / 12.0
        number_of_payments = loan_term_years * 12

        if number_of_payments == 0:
            return 0.0 if principal <= balloon_payment else float('inf')

        pv_balloon_payment = 0.0
        if balloon_payment > 0:
            if monthly_interest_rate > 0:
                try:
                    pv_balloon_payment = balloon_payment / math.pow(1 + monthly_interest_rate, number_of_payments)
                except OverflowError: 
                    pv_balloon_payment = 0 
            else: 
                pv_balloon_payment = balloon_payment
        
        effective_principal = principal - pv_balloon_payment

        if effective_principal <= 0: 
            return 0.0

        if monthly_interest_rate == 0:
            return effective_principal / number_of_payments if number_of_payments > 0 else 0.0

        try:
            payment = effective_principal * (monthly_interest_rate * math.pow(1 + monthly_interest_rate, number_of_payments)) / \
                      (math.pow(1 + monthly_interest_rate, number_of_payments) - 1)
        except (OverflowError, ZeroDivisionError):
            payment = float('inf') 
        
        return payment if payment > 1e-6 else 0.0


    def get_cost_breakdown_for_chart(self, total_months_car_lifetime: int) -> dict:
        monthly_data_list = []
        _monthly_loan_payment_val = self._calculate_monthly_loan_payment()
        financing_duration_months = self.financing.duration_years * 12
        
        grand_total_lifetime_cost = 0.0
        # Summen für einzelne Kostenkomponenten
        total_financing_component = 0.0
        total_operation_component = 0.0
        total_insurance_component = 0.0
        total_fuel_component = 0.0

        for month_num in range(1, total_months_car_lifetime + 1):
            current_year_index = (month_num - 1) // 12
            inflation_factor = math.pow(1 + (self.operating_cost_increase_percent / 100.0), current_year_index)

            actual_financing_this_month = 0.0
            if month_num <= financing_duration_months:
                actual_financing_this_month = _monthly_loan_payment_val
                if month_num == financing_duration_months and self.financing.balloon_payment > 0:
                    actual_financing_this_month += self.financing.balloon_payment
            
            financing_share_for_bar = 0.0
            if month_num <= financing_duration_months:
                financing_share_for_bar = _monthly_loan_payment_val

            current_monthly_running_costs = self.car.running_costs_monthly * inflation_factor
            operation_share = current_monthly_running_costs

            current_monthly_insurance_cost = self.insurance.get_monthly_cost() * inflation_factor
            insurance_share = current_monthly_insurance_cost
            
            current_fuel_price = self.fuel_price_per_liter * inflation_factor
            fuel_costs_share = 0.0
            if self.car.consumption_per_100km > 0 and self.km_per_month > 0:
                fuel_costs_share = (self.km_per_month / 100.0) * self.car.consumption_per_100km * current_fuel_price
            
            total_monthly_cost_for_bar = financing_share_for_bar + operation_share + insurance_share + fuel_costs_share
            
            # Aufaddieren zu den Gesamtsummen der Komponenten
            # Wichtig: total_financing_component summiert die *tatsächlichen* Finanzierungskosten inkl. Schlussrate
            total_financing_component += actual_financing_this_month
            total_operation_component += operation_share
            total_insurance_component += insurance_share
            total_fuel_component += fuel_costs_share
            
            grand_total_lifetime_cost += actual_financing_this_month + operation_share + insurance_share + fuel_costs_share

            monthly_data_list.append({
                "month": month_num,
                "financing": round(financing_share_for_bar, 2),
                "operation": round(operation_share, 2),
                "insurance": round(insurance_share, 2),
                "fuel": round(fuel_costs_share, 2),
                "total": round(total_monthly_cost_for_bar, 2) 
            })
        
        component_totals = {
            "financing": round(total_financing_component, 2),
            "operation": round(total_operation_component, 2),
            "insurance": round(total_insurance_component, 2),
            "fuel": round(total_fuel_component, 2)
        }
        
        return {
            "monthly_data": monthly_data_list,
            "total_lifetime_cost": round(grand_total_lifetime_cost, 2),
            "component_totals": component_totals # NEU
        }