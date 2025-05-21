# src/financing.py
class Financing:
    def __init__(self,
                 interest_rate_percent: float = 0.0,
                 duration_years: int = 0):
        """
        Initialisiert ein Finanzierungs-Objekt.

        Args:
            interest_rate_percent (float): Jährlicher Zinssatz in Prozent.
            duration_years (int): Laufzeit der Finanzierung in Jahren.
        """
        self.interest_rate_percent = interest_rate_percent
        self.duration_years = duration_years

    def __str__(self):
        return (f"Finanzierung(Zinssatz: {self.interest_rate_percent}%, "
                f"Laufzeit: {self.duration_years} Jahre)")