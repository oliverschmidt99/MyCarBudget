# src/car.py
class Car:
    def __init__(self,
                 purchase_price: float = 0.0,
                 running_costs_monthly: float = 0.0,
                 consumption_per_100km: float = 0.0):
        """
        Initialisiert ein Auto-Objekt.

        Args:
            purchase_price (float): Kaufpreis des Autos in €.
            running_costs_monthly (float): Betriebskosten pro Monat in € (Versicherung, Steuer, Wartung etc.).
            consumption_per_100km (float): Kraftstoffverbrauch auf 100 km (z.B. in Litern).
        """
        self.purchase_price = purchase_price
        self.running_costs_monthly = running_costs_monthly
        self.consumption_per_100km = consumption_per_100km

    def __str__(self):
        return (f"Auto(Kaufpreis: {self.purchase_price}€, "
                f"Betriebskosten: {self.running_costs_monthly}€/Monat, "
                f"Verbrauch: {self.consumption_per_100km}/100km)")