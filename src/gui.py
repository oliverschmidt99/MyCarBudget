# src/gui.py
import tkinter as tk
from tkinter import ttk, messagebox
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np # Hinzugefügt für numpy Array Operationen im Chart

from .car import Car
from .financing import Financing
from .calculator import CostCalculator
from .insurance import Insurance # NEUER Import

# Standard-Konfigurationsdatei (optional, für späteres Speichern/Laden)
# import json
# CONFIG_FILE = "car_cost_config.json"

class CarCostGUI:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title("Autokostenrechner")
        self.root.geometry("900x650") # Etwas höher für das neue Feld

        # Instanzen für Parameter
        self.car_params = Car()
        self.financing_params = Financing()
        self.insurance_params = Insurance() # NEUE Instanz für Versicherung
        
        # Zusätzliche Nutzungsparameter
        self.km_per_year_var = tk.DoubleVar(value=15000.0)
        self.fuel_price_var = tk.DoubleVar(value=1.70)
        self.car_lifetime_years_var = tk.IntVar(value=10)
        self.operating_cost_increase_var = tk.DoubleVar(value=2.0) # z.B. 2% p.a.
        self.insurance_annual_cost_var = tk.DoubleVar(value=600.0) # NEUE Variable für GUI

        self._setup_ui()
        # self._load_parameters_on_startup() # Optional

    def _get_float_from_entry(self, entry_widget, default_value=0.0, error_title="Eingabefehler", field_name=""):
        try:
            value_str = entry_widget.get().replace(",", ".")
            if not value_str:
                return default_value
            return float(value_str)
        except ValueError:
            messagebox.showerror(error_title, f"Ungültiger Wert für '{field_name}': '{entry_widget.get()}'. Bitte eine Zahl eingeben.")
            entry_widget.focus_set()
            raise ValueError(f"Ungültiger Wert für {field_name}")

    def _get_int_from_entry(self, entry_widget, default_value=0, error_title="Eingabefehler", field_name=""):
        try:
            value_str = entry_widget.get()
            if not value_str:
                return default_value
            return int(value_str)
        except ValueError:
            messagebox.showerror(error_title, f"Ungültiger Wert für '{field_name}': '{entry_widget.get()}'. Bitte eine ganze Zahl eingeben.")
            entry_widget.focus_set()
            raise ValueError(f"Ungültiger Wert für {field_name}")

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        input_frame = ttk.LabelFrame(main_frame, text="Eingabeparameter", padding="10")
        input_frame.grid(row=0, column=0, padx=(0,10), pady=5, sticky="nswe")
        input_frame.columnconfigure(1, weight=1)

        row_idx = 0
        # Auto Parameter
        ttk.Label(input_frame, text="Kaufpreis Auto (€):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_purchase_price = ttk.Entry(input_frame, width=25)
        self.entry_purchase_price.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        self.entry_purchase_price.insert(0, "25000.0")
        row_idx += 1

        ttk.Label(input_frame, text="Betriebskosten (€/Monat):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_running_costs = ttk.Entry(input_frame)
        self.entry_running_costs.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        self.entry_running_costs.insert(0, "150.0") # Beispielwert, da Versicherung jetzt separat
        row_idx += 1

        # NEUES VERSICHERUNGSFELD
        ttk.Label(input_frame, text="Versicherungskosten (€/Jahr):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_insurance_annual_cost = ttk.Entry(input_frame, textvariable=self.insurance_annual_cost_var)
        self.entry_insurance_annual_cost.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        row_idx += 1

        ttk.Label(input_frame, text="Verbrauch (Liter/100km):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_consumption = ttk.Entry(input_frame)
        self.entry_consumption.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        self.entry_consumption.insert(0, "7.0")
        row_idx += 1

        # Nutzungs Parameter
        ttk.Label(input_frame, text="Jahreskilometerleistung (km):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_km_per_year = ttk.Entry(input_frame, textvariable=self.km_per_year_var)
        self.entry_km_per_year.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        row_idx += 1

        ttk.Label(input_frame, text="Kraftstoffpreis (€/Liter):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_fuel_price = ttk.Entry(input_frame, textvariable=self.fuel_price_var)
        self.entry_fuel_price.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        row_idx += 1

        ttk.Label(input_frame, text="Geplante Haltedauer (Jahre):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_car_lifetime_years = ttk.Entry(input_frame, textvariable=self.car_lifetime_years_var)
        self.entry_car_lifetime_years.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        row_idx += 1
        
        ttk.Label(input_frame, text="Preissteigerung p.a. (%):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_op_cost_increase = ttk.Entry(input_frame, textvariable=self.operating_cost_increase_var)
        self.entry_op_cost_increase.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        # Tooltip aktualisiert
        tooltip_op_cost = tk.Label(input_frame, text="Für Betriebskosten, Versicherung & Kraftstoff", relief=tk.SUNKEN, bd=1, font=('Helvetica', 8))
        tooltip_op_cost.grid(row=row_idx, column=2, sticky="w", padx=5)
        row_idx += 1

        # Finanzierungs Parameter
        ttk.Label(input_frame, text="Zinsen Finanzierung (eff. % p.a.):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_interest_rate = ttk.Entry(input_frame)
        self.entry_interest_rate.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        self.entry_interest_rate.insert(0, "3.5")
        row_idx += 1

        ttk.Label(input_frame, text="Dauer Finanzierung (Jahre):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_financing_duration = ttk.Entry(input_frame)
        self.entry_financing_duration.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        self.entry_financing_duration.insert(0, "5")
        row_idx += 1

        control_frame = ttk.Frame(input_frame)
        control_frame.grid(row=row_idx, column=0, columnspan=3, pady=10, sticky="ew")

        self.btn_calculate = ttk.Button(control_frame, text="Berechnen", command=self._trigger_calculation)
        self.btn_calculate.pack(side="left", padx=5)

        self.chart_frame = ttk.LabelFrame(main_frame, text="Kostendiagramm (Monatlich)", padding="10")
        self.chart_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")
        
        self.chart_canvas_placeholder = tk.Label(self.chart_frame, text="Diagramm wird hier angezeigt.\n(Matplotlib-Integration erforderlich)", background="lightgrey", anchor="center")
        self.chart_canvas_placeholder.pack(expand=True, fill="both")

        main_frame.columnconfigure(0, weight=1) 
        main_frame.columnconfigure(1, weight=2) 
        main_frame.rowconfigure(0, weight=1)

    def _trigger_calculation(self):
        try:
            self.car_params.purchase_price = self._get_float_from_entry(self.entry_purchase_price, 0.0, field_name="Kaufpreis")
            self.car_params.running_costs_monthly = self._get_float_from_entry(self.entry_running_costs, 0.0, field_name="Betriebskosten")
            
            # Versicherungsparameter einlesen
            self.insurance_params.annual_cost = self.insurance_annual_cost_var.get() # Nimmt Wert aus tk.DoubleVar
            if self.insurance_params.annual_cost < 0:
                messagebox.showerror("Fehler", "Versicherungskosten dürfen nicht negativ sein.")
                return

            self.car_params.consumption_per_100km = self._get_float_from_entry(self.entry_consumption, 0.0, field_name="Verbrauch")

            km_per_year_val = self.km_per_year_var.get()
            fuel_price_val = self.fuel_price_var.get()
            car_lifetime_val = self.car_lifetime_years_var.get()
            op_cost_increase_val = self.operating_cost_increase_var.get()

            self.financing_params.interest_rate_percent = self._get_float_from_entry(self.entry_interest_rate, 0.0, field_name="Zinssatz")
            self.financing_params.duration_years = self._get_int_from_entry(self.entry_financing_duration, 0, field_name="Finanzierungsdauer")

            if self.car_params.purchase_price < 0 or self.financing_params.duration_years < 0 or car_lifetime_val <= 0:
                 # Fehlermeldungen für spezifische Felder werden bereits in get_float/int_from_entry behandelt
                 # Hier könnte eine allgemeine Prüfung oder Bestätigung erfolgen, ist aber optional
                 pass


            calculator = CostCalculator(
                car=self.car_params,
                financing=self.financing_params,
                insurance=self.insurance_params, # Versicherungsobjekt übergeben
                km_per_year=km_per_year_val,
                fuel_price_per_liter=fuel_price_val,
                operating_cost_increase_percent=op_cost_increase_val
            )

            total_months_for_chart = car_lifetime_val * 12
            chart_data = calculator.get_cost_breakdown_for_chart(total_months_for_chart)

            self._update_chart(chart_data)
            
        except ValueError: 
            print(f"Berechnung abgebrochen aufgrund ungültiger Eingabe.")
        except Exception as e:
            messagebox.showerror("Unerwarteter Fehler", f"Ein Fehler ist aufgetreten: {str(e)}")


    def _update_chart(self, data: list):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not data:
            tk.Label(self.chart_frame, text="Keine Daten zum Anzeigen.").pack(expand=True, fill="both")
            return

        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            # numpy ist bereits oben importiert

            fig = Figure(figsize=(6, 5), dpi=100) # Ggf. Größe anpassen
            ax = fig.add_subplot(111)

            months = [item['month'] for item in data]
            financing_costs = np.array([item['financing'] for item in data])
            operation_costs = np.array([item['operation'] for item in data])
            # Versicherungskosten aus Daten holen, mit Standardwert 0.0 falls nicht vorhanden
            insurance_costs = np.array([item.get('insurance', 0.0) for item in data]) 
            fuel_costs = np.array([item['fuel'] for item in data])

            bar_width = 0.8
            # Gestapelte Balken
            ax.bar(months, financing_costs, bar_width, label='Finanzierung', color='skyblue')
            
            bottom_op = financing_costs
            ax.bar(months, operation_costs, bar_width, bottom=bottom_op, label='Betriebskosten', color='orange')
            
            bottom_ins = bottom_op + operation_costs
            ax.bar(months, insurance_costs, bar_width, bottom=bottom_ins, label='Versicherung', color='lightcoral') # Neue Farbe für Versicherung
            
            bottom_fuel = bottom_ins + insurance_costs
            ax.bar(months, fuel_costs, bar_width, bottom=bottom_fuel, label='Kraftstoff', color='green')

            ax.set_xlabel("Monat")
            ax.set_ylabel("Kosten (€)")
            ax.set_title("Monatliche Autokosten")
            ax.legend(loc='upper left') # Legende angepasst
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas.draw()

        except ImportError:
            placeholder_text = f"Matplotlib nicht gefunden.\n{len(data)} Monate berechnet.\nErster Monat Gesamt: {data[0]['total']:.2f}€\n(Details: F:{data[0]['financing']:.2f}, B:{data[0]['operation']:.2f}, V:{data[0].get('insurance',0):.2f}, K:{data[0]['fuel']:.2f})"
            tk.Label(self.chart_frame, text=placeholder_text, justify=tk.LEFT).pack(expand=True, fill="both")
        except Exception as e:
            tk.Label(self.chart_frame, text=f"Fehler beim Erstellen des Diagramms: {e}").pack(expand=True, fill="both")

    # Speicher- und Ladefunktionen (Platzhalter)
    # ... (bleiben unverändert) ...