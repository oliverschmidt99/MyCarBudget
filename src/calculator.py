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
        # ... (Diese Methode bleibt unverändert wie in der vorherigen Version) ...
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

        for month_num in range(1, total_months_car_lifetime + 1):
            current_year_index = (month_num - 1) // 12
            inflation_factor = math.pow(1 + (self.operating_cost_increase_percent / 100.0), current_year_index)

            # Tatsächliche Finanzierungskosten diesen Monat (für die Gesamtsumme)
            actual_financing_this_month = 0.0
            if month_num <= financing_duration_months:
                actual_financing_this_month = _monthly_loan_payment_val
                if month_num == financing_duration_months and self.financing.balloon_payment > 0:
                    actual_financing_this_month += self.financing.balloon_payment # Hinzufügen zur Gesamtsumme
            
            # Finanzierungsanteil für den Balken im Diagramm (OHNE Schlussrate)
            financing_share_for_bar = 0.0
            if month_num <= financing_duration_months:
                financing_share_for_bar = _monthly_loan_payment_val # Nur die reguläre Rate für den Balken

            current_monthly_running_costs = self.car.running_costs_monthly * inflation_factor
            operation_share = current_monthly_running_costs

            current_monthly_insurance_cost = self.insurance.get_monthly_cost() * inflation_factor
            insurance_share = current_monthly_insurance_cost
            
            current_fuel_price = self.fuel_price_per_liter * inflation_factor
            fuel_costs_share = 0.0
            if self.car.consumption_per_100km > 0 and self.km_per_month > 0:
                fuel_costs_share = (self.km_per_month / 100.0) * self.car.consumption_per_100km * current_fuel_price
            
            # Monatliche Gesamtkosten für den Balken (Summe der im Balken gezeigten Komponenten)
            total_monthly_cost_for_bar = financing_share_for_bar + operation_share + insurance_share + fuel_costs_share
            
            # Aufaddieren der tatsächlichen Kosten zur Gesamtlebensdauersumme
            # Die Anteile für Betrieb, Versicherung und Kraftstoff sind für beide Berechnungen (Balken vs. Gesamtsumme) gleich.
            # Der Unterschied liegt nur im Finanzierungsanteil, wenn die Schlussrate fällig ist.
            grand_total_lifetime_cost += actual_financing_this_month + operation_share + insurance_share + fuel_costs_share

            monthly_data_list.append({
                "month": month_num,
                "financing": round(financing_share_for_bar, 2), # Dieser Wert geht in den Balken
                "operation": round(operation_share, 2),
                "insurance": round(insurance_share, 2),
                "fuel": round(fuel_costs_share, 2),
                "total": round(total_monthly_cost_for_bar, 2) # 'total' spiegelt die Summe der Balkenkomponenten wider
            })
        
        return {
            "monthly_data": monthly_data_list,
            "total_lifetime_cost": round(grand_total_lifetime_cost, 2) # Dies sind die wahren Gesamtkosten
        }