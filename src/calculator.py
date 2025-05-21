# src/calculator.py
from .car import Car
from .financing import Financing
from .insurance import Insurance # NEUER Import
import math

class CostCalculator:
    def __init__(self,
                 car: Car,
                 financing: Financing,
                 insurance: Insurance, # NEUER Parameter
                 km_per_year: float,
                 fuel_price_per_liter: float,
                 operating_cost_increase_percent: float):
        self.car = car
        self.financing = financing
        self.insurance = insurance # Versicherungsobjekt speichern
        self.km_per_year = km_per_year
        self.fuel_price_per_liter = fuel_price_per_liter
        self.operating_cost_increase_percent = operating_cost_increase_percent
        self.km_per_month = self.km_per_year / 12.0 if self.km_per_year else 0.0

    def _calculate_monthly_loan_payment(self) -> float:
        # ... (bleibt unverändert) ...
        principal = self.car.purchase_price
        annual_interest_rate = self.financing.interest_rate_percent / 100.0
        loan_term_years = self.financing.duration_years

        if loan_term_years <= 0 or principal <= 0:
            return 0.0
        if annual_interest_rate == 0:
            return principal / (loan_term_years * 12.0)

        monthly_interest_rate = annual_interest_rate / 12.0
        number_of_payments = loan_term_years * 12
        
        if monthly_interest_rate == 0:
             return principal / number_of_payments
        try:
            payment = principal * (monthly_interest_rate * math.pow(1 + monthly_interest_rate, number_of_payments)) / \
                      (math.pow(1 + monthly_interest_rate, number_of_payments) - 1)
        except (OverflowError, ZeroDivisionError): 
            payment = principal / number_of_payments if number_of_payments > 0 else float('inf')
        return payment


    def get_cost_breakdown_for_chart(self, total_months_car_lifetime: int) -> list:
        chart_data = []
        # Die monatliche Kreditrate wird nur einmal berechnet, wenn sie benötigt wird (innerhalb der Schleife)
        # oder hier, falls sie konstant ist und nicht von month_num abhängt.
        # Für feste Raten ist es effizienter, sie außerhalb der Schleife zu berechnen.
        _monthly_loan_payment_val = self._calculate_monthly_loan_payment()


        for month_num in range(1, total_months_car_lifetime + 1):
            current_year_index = (month_num - 1) // 12
            inflation_factor = math.pow(1 + (self.operating_cost_increase_percent / 100.0), current_year_index)

            # 1. Finanzierungskosten
            financing_share = 0.0
            if month_num <= self.financing.duration_years * 12:
                financing_share = _monthly_loan_payment_val # Verwende den vorberechneten Wert

            # 2. Betriebskosten (mit Inflation)
            # Annahme: self.car.running_costs_monthly sind die Kosten OHNE Versicherung
            current_monthly_running_costs = self.car.running_costs_monthly * inflation_factor
            operation_share = current_monthly_running_costs

            # 3. Versicherungskosten (mit Inflation)
            current_monthly_insurance_cost = self.insurance.get_monthly_cost() * inflation_factor
            insurance_share = current_monthly_insurance_cost
            
            # 4. Kraftstoffkosten (mit Inflation auf den Kraftstoffpreis)
            current_fuel_price = self.fuel_price_per_liter * inflation_factor
            fuel_costs_share = 0.0
            if self.car.consumption_per_100km > 0 and self.km_per_month > 0:
                fuel_costs_share = (self.km_per_month / 100.0) * self.car.consumption_per_100km * current_fuel_price
            
            total_monthly_cost = financing_share + operation_share + insurance_share + fuel_costs_share

            chart_data.append({
                "month": month_num,
                "financing": round(financing_share, 2),
                "operation": round(operation_share, 2),
                "insurance": round(insurance_share, 2), # NEUES Feld für Diagrammdaten
                "fuel": round(fuel_costs_share, 2),
                "total": round(total_monthly_cost, 2)
            })
        return chart_data