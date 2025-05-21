# src/gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import json
import math
import os # Hinzugefügt für Dateipfade

from .car import Car
from .financing import Financing
from .calculator import CostCalculator
from .insurance import Insurance

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter

# Pfad zur Speicherdatei im Projekt-Stammverzeichnis (cost_car_calc/data.json)
# __file__ ist der Pfad zu gui.py (in src), also '..' um ins Projekt-Stammverzeichnis zu gelangen
DATA_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data.json'))


class CarCostGUI:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title("Autokostenrechner")
        self.root.geometry("950x800") # Höhe leicht angepasst für neue UI-Elemente

        self.car_params = Car()
        self.financing_params = Financing()
        self.insurance_params = Insurance()
        
        self.km_per_year_var = tk.DoubleVar(value=15000.0)
        self.fuel_price_var = tk.DoubleVar(value=1.70)
        self.car_lifetime_years_var = tk.IntVar(value=10)
        self.operating_cost_increase_var = tk.DoubleVar(value=2.0)
        self.insurance_annual_cost_var = tk.DoubleVar(value=600.0)
        self.balloon_payment_var = tk.DoubleVar(value=0.0)
        self.total_lifetime_cost_var = tk.StringVar(value="Gesamtkosten: N/A")

        # Für das neue Speichern/Laden
        self.config_name_var = tk.StringVar()
        self.saved_configs_list = [] # Liste der Namen gespeicherter Konfigurationen

        self._setup_ui()
        self._update_saved_configs_dropdown() # Gespeicherte Konfigurationen beim Start laden


    def _get_data_filepath(self):
        """Gibt den Pfad zur data.json zurück und stellt sicher, dass das Verzeichnis existiert."""
        # Da DATA_FILE_PATH bereits absolut ist und das Stammverzeichnis nutzt,
        # ist keine weitere Verzeichniserstellung nötig, wenn das Projekt korrekt strukturiert ist.
        return DATA_FILE_PATH

    def _read_data_file(self) -> dict:
        """Liest die data.json und gibt den Inhalt als Dictionary zurück."""
        filepath = self._get_data_filepath()
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {} # Leeres Dict, wenn Datei nicht existiert
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Fehler beim Lesen der Speicherdatei", 
                                 f"Konnte '{filepath}' nicht laden oder parsen.\n{e}")
            return {}

    def _write_data_file(self, data: dict):
        """Schreibt das übergebene Dictionary in die data.json."""
        filepath = self._get_data_filepath()
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            messagebox.showerror("Fehler beim Schreiben der Speicherdatei",
                                 f"Konnte nicht in '{filepath}' schreiben.\n{e}")

    def _update_saved_configs_dropdown(self):
        """Aktualisiert die Dropdown-Liste der gespeicherten Konfigurationen."""
        all_configs = self._read_data_file()
        self.saved_configs_list = sorted(list(all_configs.keys()))
        self.combo_saved_configs['values'] = self.saved_configs_list
        if self.saved_configs_list:
            self.combo_saved_configs.current(0) # Wähle das erste Element standardmäßig aus
        else:
            self.combo_saved_configs.set('') # Leere Combobox, wenn keine Konfigs vorhanden

    def _get_float_from_entry(self, entry_widget, default_value=0.0, error_title="Eingabefehler", field_name="Feld"):
        # ... (unverändert) ...
        try:
            value_str = entry_widget.get().replace(",", ".")
            if not value_str:
                entry_widget.state(['!invalid'])
                return default_value
            val = float(value_str)
            entry_widget.state(['!invalid'])
            return val
        except ValueError:
            entry_widget.state(['invalid'])
            messagebox.showerror(error_title, f"Ungültiger Wert für '{field_name}': '{entry_widget.get()}'. Bitte eine Zahl eingeben.")
            entry_widget.focus_set()
            raise ValueError(f"Ungültiger Wert für {field_name}")


    def _get_int_from_entry(self, entry_widget, default_value=0, error_title="Eingabefehler", field_name="Feld"):
        # ... (unverändert) ...
        try:
            value_str = entry_widget.get()
            if not value_str:
                entry_widget.state(['!invalid'])
                return default_value
            val = int(value_str)
            entry_widget.state(['!invalid'])
            return val
        except ValueError:
            entry_widget.state(['invalid'])
            messagebox.showerror(error_title, f"Ungültiger Wert für '{field_name}': '{entry_widget.get()}'. Bitte eine ganze Zahl eingeben.")
            entry_widget.focus_set()
            raise ValueError(f"Ungültiger Wert für {field_name}")

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=0) 
        main_frame.rowconfigure(1, weight=0) 
        main_frame.rowconfigure(2, weight=0) # NEUE Zeile für Speichern/Laden UI

        input_frame = ttk.LabelFrame(main_frame, text="Eingabeparameter", padding="10")
        input_frame.grid(row=0, column=0, padx=(0,10), pady=5, sticky="nswe")
        input_frame.columnconfigure(1, weight=1)

        row_idx = 0
        # ... (Alle Eingabefelder für Auto, Nutzung, Finanzierung etc. wie zuvor) ...
        # Auto Parameter
        ttk.Label(input_frame, text="Kaufpreis Auto (€):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_purchase_price = ttk.Entry(input_frame, width=25)
        self.entry_purchase_price.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        self.entry_purchase_price.insert(0, "25000.0")
        row_idx += 1
        # ... (Rest der Eingabefelder) ...
        ttk.Label(input_frame, text="Betriebskosten (€/Monat):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_running_costs = ttk.Entry(input_frame)
        self.entry_running_costs.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        self.entry_running_costs.insert(0, "150.0")
        row_idx += 1

        ttk.Label(input_frame, text="Versicherungskosten (€/Jahr):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_insurance_annual_cost = ttk.Entry(input_frame, textvariable=self.insurance_annual_cost_var)
        self.entry_insurance_annual_cost.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        row_idx += 1

        ttk.Label(input_frame, text="Verbrauch (Liter/100km):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_consumption = ttk.Entry(input_frame)
        self.entry_consumption.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        self.entry_consumption.insert(0, "7.0")
        row_idx += 1

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
        tooltip_op_cost = tk.Label(input_frame, text="Für Betriebskosten, Versicherung & Kraftstoff", relief=tk.SUNKEN, bd=1, font=('Helvetica', 8))
        tooltip_op_cost.grid(row=row_idx, column=2, sticky="w", padx=5)
        row_idx += 1

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

        ttk.Label(input_frame, text="Schlussrate (€, optional):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.entry_balloon_payment = ttk.Entry(input_frame, textvariable=self.balloon_payment_var)
        self.entry_balloon_payment.grid(row=row_idx, column=1, sticky="we", padx=5, pady=3)
        row_idx += 1
        
        # --- Berechnen Button ---
        # Wird nun im save_load_frame platziert oder bleibt hier, je nach Design
        self.btn_calculate = ttk.Button(input_frame, text="Berechnen", command=self._trigger_calculation)
        self.btn_calculate.grid(row=row_idx, column=0, columnspan=3, pady=(10,0), sticky="ew")
        # row_idx += 1 # Falls weitere Elemente im input_frame folgen

        # --- Speicher/Lade Frame (unterhalb des Input Frames, aber über Summary) ---
        save_load_frame = ttk.LabelFrame(main_frame, text="Konfigurationen", padding="10")
        save_load_frame.grid(row=1, column=0, padx=(0,10), pady=5, sticky="new")
        save_load_frame.columnconfigure(1, weight=1) # Damit Entry und Combobox wachsen

        ttk.Label(save_load_frame, text="Name zum Speichern:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.entry_config_name = ttk.Entry(save_load_frame, textvariable=self.config_name_var, width=30)
        self.entry_config_name.grid(row=0, column=1, padx=5, pady=3, sticky="we")
        self.btn_save_config = ttk.Button(save_load_frame, text="Speichern", command=self._save_current_configuration)
        self.btn_save_config.grid(row=0, column=2, padx=5, pady=3)
        
        ttk.Label(save_load_frame, text="Gespeichert:").grid(row=1, column=0, padx=5, pady=3, sticky="w")
        self.combo_saved_configs = ttk.Combobox(save_load_frame, values=self.saved_configs_list, state="readonly", width=28)
        self.combo_saved_configs.grid(row=1, column=1, padx=5, pady=3, sticky="we")
        self.btn_load_config = ttk.Button(save_load_frame, text="Laden", command=self._load_selected_configuration)
        self.btn_load_config.grid(row=1, column=2, padx=5, pady=3)


        # --- Summary Frame (unterhalb des Speicher/Lade Frames) ---
        summary_frame = ttk.LabelFrame(main_frame, text="Zusammenfassung", padding="10")
        summary_frame.grid(row=2, column=0, padx=(0,10), pady=(5,5), sticky="new")
        
        self.label_total_lifetime_cost = ttk.Label(summary_frame, textvariable=self.total_lifetime_cost_var, font=("Helvetica", 12, "bold"))
        self.label_total_lifetime_cost.pack(pady=5, anchor="w")


        # --- Chart Display Frame (rechts, erstreckt sich über alle drei Zeilen links) ---
        self.chart_frame = ttk.LabelFrame(main_frame, text="Kostendiagramm", padding="10")
        self.chart_frame.grid(row=0, column=1, rowspan=3, padx=5, pady=5, sticky="nsew")
        
        self.chart_canvas_placeholder = tk.Label(self.chart_frame, text="Diagramm wird hier angezeigt.", background="lightgrey", anchor="center")
        self.chart_canvas_placeholder.pack(expand=True, fill="both")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)


    def _collect_parameters_for_saving(self) -> dict:
        """Sammelt die aktuellen Parameter aus der GUI für das Speichern."""
        # Diese Methode löst bei Fehlern eine ValueError aus, die von der aufrufenden Methode behandelt wird.
        params_to_save = {
            "car_purchase_price": self._get_float_from_entry(self.entry_purchase_price, field_name="Kaufpreis"),
            "car_running_costs_monthly": self._get_float_from_entry(self.entry_running_costs, field_name="Betriebskosten"),
            "car_consumption_per_100km": self._get_float_from_entry(self.entry_consumption, field_name="Verbrauch"),
            
            "financing_interest_rate_percent": self._get_float_from_entry(self.entry_interest_rate, field_name="Zinssatz"),
            "financing_duration_years": self._get_int_from_entry(self.entry_financing_duration, field_name="Finanzierungsdauer"),
            "financing_balloon_payment": self.balloon_payment_var.get(), # tk.DoubleVar
            
            "insurance_annual_cost": self.insurance_annual_cost_var.get(), # tk.DoubleVar
            
            "usage_km_per_year": self.km_per_year_var.get(), # tk.DoubleVar
            "usage_fuel_price_per_liter": self.fuel_price_var.get(), # tk.DoubleVar
            "usage_car_lifetime_years": self.car_lifetime_years_var.get(), # tk.IntVar
            "general_operating_cost_increase_percent": self.operating_cost_increase_var.get(), # tk.DoubleVar
        }
        return params_to_save

    def _save_current_configuration(self):
        config_name = self.config_name_var.get().strip()
        if not config_name:
            messagebox.showerror("Fehler beim Speichern", "Bitte einen Namen für die Konfiguration eingeben.")
            self.entry_config_name.focus_set()
            return

        try:
            current_params = self._collect_parameters_for_saving() # Validiert Eingaben erneut
            
            all_configs = self._read_data_file()
            
            if config_name in all_configs:
                if not messagebox.askyesno("Überschreiben", 
                                           f"Die Konfiguration '{config_name}' existiert bereits.\n"
                                           "Möchten Sie sie überschreiben?"):
                    return

            all_configs[config_name] = current_params
            self._write_data_file(all_configs)
            
            messagebox.showinfo("Gespeichert", f"Konfiguration '{config_name}' erfolgreich gespeichert.")
            self._update_saved_configs_dropdown()
            # Optional: Die Combobox auf den neu gespeicherten Namen setzen
            if config_name in self.saved_configs_list:
                self.combo_saved_configs.set(config_name)

        except ValueError: # Von _collect_parameters_for_saving
             messagebox.showwarning("Speichern abgebrochen", 
                                    "Bitte korrigieren Sie die Eingabefehler (rot markiert), bevor Sie speichern.")
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", f"Ein unerwarteter Fehler ist aufgetreten:\n{str(e)}")


    def _load_selected_configuration(self):
        selected_name = self.combo_saved_configs.get()
        if not selected_name:
            messagebox.showinfo("Laden", "Bitte wählen Sie eine Konfiguration aus der Liste aus.")
            return

        all_configs = self._read_data_file()
        loaded_params = all_configs.get(selected_name)

        if not loaded_params:
            messagebox.showerror("Fehler beim Laden", f"Konfiguration '{selected_name}' nicht in der Datei gefunden.")
            self._update_saved_configs_dropdown() # Liste aktualisieren, falls Datei inkonsistent
            return
        
        try:
            # GUI Felder mit geladenen Werten füllen
            self.entry_purchase_price.delete(0, tk.END)
            self.entry_purchase_price.insert(0, str(loaded_params.get("car_purchase_price", 0.0)))
            self.entry_running_costs.delete(0, tk.END)
            self.entry_running_costs.insert(0, str(loaded_params.get("car_running_costs_monthly", 0.0)))
            self.entry_consumption.delete(0, tk.END)
            self.entry_consumption.insert(0, str(loaded_params.get("car_consumption_per_100km", 0.0)))
            
            self.entry_interest_rate.delete(0, tk.END)
            self.entry_interest_rate.insert(0, str(loaded_params.get("financing_interest_rate_percent", 0.0)))
            self.entry_financing_duration.delete(0, tk.END)
            self.entry_financing_duration.insert(0, str(loaded_params.get("financing_duration_years", 0)))
            
            self.balloon_payment_var.set(loaded_params.get("financing_balloon_payment", 0.0))
            self.insurance_annual_cost_var.set(loaded_params.get("insurance_annual_cost", 0.0))
            self.km_per_year_var.set(loaded_params.get("usage_km_per_year", 15000.0))
            self.fuel_price_var.set(loaded_params.get("usage_fuel_price_per_liter", 1.70))
            self.car_lifetime_years_var.set(loaded_params.get("usage_car_lifetime_years", 10))
            self.operating_cost_increase_var.set(loaded_params.get("general_operating_cost_increase_percent", 2.0))
            
            self.config_name_var.set(selected_name) # Den geladenen Namen ins Eingabefeld setzen

            # Reset background colors (states) after loading
            all_entries = [
                self.entry_purchase_price, self.entry_running_costs, self.entry_insurance_annual_cost,
                self.entry_consumption, self.entry_km_per_year, self.entry_fuel_price,
                self.entry_car_lifetime_years, self.entry_op_cost_increase, self.entry_interest_rate,
                self.entry_financing_duration, self.entry_balloon_payment
            ]
            for entry_widget in all_entries:
                if isinstance(entry_widget, ttk.Entry):
                    entry_widget.state(['!invalid'])


            messagebox.showinfo("Geladen", f"Konfiguration '{selected_name}' erfolgreich geladen.")
            self._trigger_calculation() # Automatisch neu berechnen und Diagramm aktualisieren

        except Exception as e:
            messagebox.showerror("Fehler beim Laden der Parameter", f"Ein unerwarteter Fehler ist aufgetreten:\n{str(e)}")


    def _trigger_calculation(self):
        # ... (Die Logik dieser Methode bleibt im Wesentlichen gleich,
        #      stellt sicher, dass die Parameter aus den GUI-Feldern korrekt
        #      in self.car_params, self.financing_params etc. geschrieben werden,
        #      bevor der Calculator aufgerufen wird.
        #      Die Aktualisierung von self.total_lifetime_cost_var ist auch hier.) ...
        try:
            all_entries = [
                self.entry_purchase_price, self.entry_running_costs, self.entry_insurance_annual_cost,
                self.entry_consumption, self.entry_km_per_year, self.entry_fuel_price,
                self.entry_car_lifetime_years, self.entry_op_cost_increase, self.entry_interest_rate,
                self.entry_financing_duration, self.entry_balloon_payment
            ]
            for entry_widget in all_entries:
                if isinstance(entry_widget, ttk.Entry):
                    entry_widget.state(['!invalid'])


            self.car_params.purchase_price = self._get_float_from_entry(self.entry_purchase_price, field_name="Kaufpreis")
            self.car_params.running_costs_monthly = self._get_float_from_entry(self.entry_running_costs, field_name="Betriebskosten")
            
            insurance_cost_val = self.insurance_annual_cost_var.get()
            if insurance_cost_val < 0:
                self.entry_insurance_annual_cost.state(['invalid']) # Markiert das Entry-Feld
                messagebox.showerror("Fehler", "Versicherungskosten dürfen nicht negativ sein.")
                return
            self.insurance_params.annual_cost = insurance_cost_val
            self.entry_insurance_annual_cost.state(['!invalid'])


            self.car_params.consumption_per_100km = self._get_float_from_entry(self.entry_consumption, field_name="Verbrauch")

            km_per_year_val = self.km_per_year_var.get()
            fuel_price_val = self.fuel_price_var.get()
            car_lifetime_val = self.car_lifetime_years_var.get()
            op_cost_increase_val = self.operating_cost_increase_var.get()

            self.financing_params.interest_rate_percent = self._get_float_from_entry(self.entry_interest_rate, field_name="Zinssatz")
            self.financing_params.duration_years = self._get_int_from_entry(self.entry_financing_duration, field_name="Finanzierungsdauer")
            
            balloon_payment_val = self.balloon_payment_var.get()
            if balloon_payment_val < 0:
                self.entry_balloon_payment.state(['invalid'])
                messagebox.showerror("Fehler", "Schlussrate darf nicht negativ sein.")
                return
            self.financing_params.balloon_payment = balloon_payment_val
            self.entry_balloon_payment.state(['!invalid'])

            if car_lifetime_val <= 0:
                 messagebox.showerror("Fehler", "Haltedauer muss größer als 0 sein.")
                 # Markiere das entsprechende Feld, falls es ein ttk.Entry ist (hier ist es an eine Variable gebunden)
                 # self.entry_car_lifetime_years.state(['invalid']) # Wenn es ein Entry wäre
                 return


            calculator = CostCalculator(
                car=self.car_params,
                financing=self.financing_params,
                insurance=self.insurance_params,
                km_per_year=km_per_year_val,
                fuel_price_per_liter=fuel_price_val,
                operating_cost_increase_percent=op_cost_increase_val
            )

            total_months_for_chart = car_lifetime_val * 12
            if total_months_for_chart <= 0:
                messagebox.showerror("Fehler", "Gesamtmonate für Diagramm müssen positiv sein (Haltedauer prüfen).")
                return

            calculation_results = calculator.get_cost_breakdown_for_chart(total_months_for_chart)
            monthly_chart_data = calculation_results["monthly_data"]
            total_lifetime_cost = calculation_results["total_lifetime_cost"]

            formatted_total_cost = f"{total_lifetime_cost:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.total_lifetime_cost_var.set(f"Gesamtkosten über Haltedauer: {formatted_total_cost} €")

            self._update_chart(monthly_chart_data)
            
        except ValueError as ve: 
            print(f"Eingabefehler in _trigger_calculation: {ve}")
        except Exception as e:
            messagebox.showerror("Unerwarteter Berechnungsfehler", f"Ein Fehler ist aufgetreten: {str(e)}")
    
    def _update_chart(self, data: list):
        # ... (Diese Methode bleibt unverändert) ...
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not data:
            tk.Label(self.chart_frame, text="Keine Daten zum Anzeigen.").pack(expand=True, fill="both")
            return
        try:
            fig = Figure(figsize=(7, 5), dpi=100)
            ax = fig.add_subplot(111)

            months = [item['month'] for item in data]
            financing_costs = np.array([item['financing'] for item in data])
            operation_costs = np.array([item['operation'] for item in data])
            insurance_costs = np.array([item.get('insurance', 0.0) for item in data]) 
            fuel_costs = np.array([item['fuel'] for item in data])

            bar_width = 0.8
            ax.bar(months, financing_costs, bar_width, label='Finanzierung', color='skyblue')
            bottom_op = financing_costs
            ax.bar(months, operation_costs, bar_width, bottom=bottom_op, label='Betriebskosten', color='orange')
            bottom_ins = bottom_op + operation_costs
            ax.bar(months, insurance_costs, bar_width, bottom=bottom_ins, label='Versicherung', color='lightcoral')
            bottom_fuel = bottom_ins + insurance_costs
            ax.bar(months, fuel_costs, bar_width, bottom=bottom_fuel, label='Kraftstoff', color='green')

            ax.set_ylabel("Kosten (€)")
            ax.set_title("Monatliche Autokosten")
            ax.legend(loc='upper left', fontsize='small')
            
            num_months_total = len(months)
            year_major_ticks = [m for m in months if (m - 1) % 12 == 0]
            if not year_major_ticks or (1 in months and year_major_ticks[0] != 1) :
                 year_major_ticks = [1] + [yt for yt in year_major_ticks if yt !=1]
            year_major_ticks = sorted(list(set(year_major_ticks)))

            year_labels = [f'Jahr {(m-1)//12 + 1}' for m in year_major_ticks]
            max_year_labels = 12
            if len(year_labels) > max_year_labels:
                step = math.ceil(len(year_labels) / max_year_labels)
                year_major_ticks = year_major_ticks[::step]
                year_labels = year_labels[::step]

            ax.set_xticks(year_major_ticks)
            ax.set_xticklabels(year_labels, rotation=30, ha='right', fontsize='small')
            ax.set_xlabel("Zeitverlauf", fontsize='medium')

            if num_months_total <= 36 : 
                ax.set_xticks(months, minor=True)
                ax.tick_params(axis='x', which='minor', labelsize='x-small', labelrotation=90)
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