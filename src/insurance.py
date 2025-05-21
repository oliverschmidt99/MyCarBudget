# src/insurance.py
class Insurance:
    def __init__(self, annual_cost: float = 0.0):
        """
        Initialisiert ein Versicherungs-Objekt.

        Args:
            annual_cost (float): Jährliche Gesamtkosten der Versicherung in €.
        """
        self.annual_cost = annual_cost

    def get_monthly_cost(self) -> float:
        """Gibt die monatlichen Versicherungskosten zurück."""
        return self.annual_cost / 12.0

    def __str__(self):
        return f"Versicherung(Jährliche Kosten: {self.annual_cost}€)"