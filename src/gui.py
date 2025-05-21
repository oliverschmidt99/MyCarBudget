# src/gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import json
import math
import os

from .car import Car
from .financing import Financing
from .calculator import CostCalculator
from .insurance import Insurance

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter

DATA_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data.json'))


class CarCostGUI:
    # ... (__init__ und andere Methoden bis _setup_ui bleiben wie in der letzten Version) ...
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title("Autokostenrechner")
        self.root.geometry("1200x900") 

        self.car_params = Car()
        self.financing_params = Financing()
        self.insurance_params = Insurance()
        
        self.km_per_year_var = tk.DoubleVar(value=15000.0)
        self.fuel_price_var = tk.DoubleVar(value=1.70)
        self.car_lifetime_years_var = tk.IntVar(value=10)
        self.operating_cost_increase_var = tk.DoubleVar(value=2.0)
        self.insurance_annual_cost_var = tk.DoubleVar(value=600.0)
        self.balloon_payment_var = tk.DoubleVar(value=0.0)
        
        self.total_lifetime_cost_var = tk.StringVar(value="Gesamtkosten (Real): N/A")
        self.total_financing_var = tk.StringVar(value="Finanzierung (Gesamt): N/A")
        self.total_operation_var = tk.StringVar(value="Betrieb (Gesamt): N/A")
        self.total_insurance_var = tk.StringVar(value="Versicherung (Gesamt): N/A")
        self.total_fuel_var = tk.StringVar(value="Kraftstoff (Gesamt): N/A")
        self.total_chart_displayed_var = tk.StringVar(value="Gesamtkosten (Diagramm): N/A")

        self.show_financing_var = tk.BooleanVar(value=True)
        self.show_operation_var = tk.BooleanVar(value=True)
        self.show_insurance_var = tk.BooleanVar(value=True)
        self.show_fuel_var = tk.BooleanVar(value=True)

        self.config_name_var = tk.StringVar()
        self.saved_configs_list = []
        
        self.calculation_results_buffer = {}

        self._setup_ui() 
        self._update_saved_configs_dropdown() 

    def _get_data_filepath(self):
        return DATA_FILE_PATH

    def _read_data_file(self) -> dict:
        filepath = self._get_data_filepath()
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {} 
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Fehler beim Lesen der Speicherdatei", 
                                 f"Konnte '{filepath}' nicht laden oder parsen.\n{e}")
            return {}

    def _write_data_file(self, data: dict):
        filepath = self._get_data_filepath()
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            messagebox.showerror("Fehler beim Schreiben der Speicherdatei",
                                 f"Konnte nicht in '{filepath}' schreiben.\n{e}")

    def _update_saved_configs_dropdown(self):
        all_configs = self._read_data_file()
        self.saved_configs_list = sorted(list(all_configs.keys()))
        self.combo_saved_configs['values'] = self.saved_configs_list
        if self.saved_configs_list:
            self.combo_saved_configs.current(0) 
        else:
            self.combo_saved_configs.set('')
            self.config_name_var.set("")

    def _get_float_from_entry(self, entry_widget, default_value=0.0, error_title="Eingabefehler", field_name="Feld"):
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
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Grid-Konfiguration für main_frame
        main_frame.columnconfigure(0, weight=3)  # Linke Spalte (Diagramm, etc.)
        main_frame.columnconfigure(1, weight=2)  # Rechte Spalte (Zusammenfassung, Eingabe)
        
        # Konfiguriere Zeilen so, dass die unterste Zeile in der linken Spalte (Konfig-Verwaltung)
        # und der Eingabe-Frame in der rechten Spalte den verfügbaren Platz ausfüllen können.
        main_frame.rowconfigure(0, weight=2)  # Diagramm / Zusammenfassung (Diagramm soll mehr Höhe bekommen)
        main_frame.rowconfigure(1, weight=0)  # Diagramm Optionen (fixe Höhe) / Start Eingabe-Frame
        main_frame.rowconfigure(2, weight=1)  # Konfig Verwalten / Rest Eingabe-Frame (flexibel)


        # === LINKE SPALTE ===

        # Diagramm (Oben Links)
        self.chart_frame = ttk.LabelFrame(main_frame, text="Monatliche Kosten im Zeitverlauf", padding="5")
        self.chart_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.chart_canvas_placeholder = tk.Label(self.chart_frame, text="Diagramm wird nach Berechnung angezeigt.", background="lightgrey", anchor="center")
        self.chart_canvas_placeholder.pack(expand=True, fill="both")

        # Diagramm Optionen (Mitte Links, unter dem Diagramm)
        chart_options_frame = ttk.LabelFrame(main_frame, text="Diagramm Optionen", padding="5")
        chart_options_frame.grid(row=1, column=0, padx=5, pady=5, sticky="new")
        cb_fin = ttk.Checkbutton(chart_options_frame, text="Finanzierung", variable=self.show_financing_var, command=self._refresh_chart_only)
        cb_fin.pack(side="left", padx=3, pady=2)
        cb_op = ttk.Checkbutton(chart_options_frame, text="Betrieb", variable=self.show_operation_var, command=self._refresh_chart_only)
        cb_op.pack(side="left", padx=3, pady=2)
        cb_ins = ttk.Checkbutton(chart_options_frame, text="Versicherung", variable=self.show_insurance_var, command=self._refresh_chart_only)
        cb_ins.pack(side="left", padx=3, pady=2)
        cb_fuel = ttk.Checkbutton(chart_options_frame, text="Kraftstoff", variable=self.show_fuel_var, command=self._refresh_chart_only)
        cb_fuel.pack(side="left", padx=3, pady=2)

        # Konfigurationen Verwalten (Unten Links)
        save_load_frame = ttk.LabelFrame(main_frame, text="Konfigurationen Verwalten", padding="10")
        save_load_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew") # geändertes sticky
        save_load_frame.columnconfigure(1, weight=1) 
        ttk.Label(save_load_frame, text="Name zum Speichern:").grid(row=0, column=0, padx=5, pady=(5,2), sticky="w")
        self.entry_config_name = ttk.Entry(save_load_frame, textvariable=self.config_name_var, width=25)
        self.entry_config_name.grid(row=0, column=1, padx=5, pady=(5,2), sticky="we")
        self.btn_save_config = ttk.Button(save_load_frame, text="Speichern", command=self._save_current_configuration, width=10)
        self.btn_save_config.grid(row=0, column=2, padx=(5,0), pady=(5,2))
        
        ttk.Label(save_load_frame, text="Gespeichert:").grid(row=1, column=0, padx=5, pady=(2,5), sticky="w")
        self.combo_saved_configs = ttk.Combobox(save_load_frame, values=self.saved_configs_list, state="readonly", width=23)
        self.combo_saved_configs.grid(row=1, column=1, padx=5, pady=(2,5), sticky="we")
        
        load_delete_frame = ttk.Frame(save_load_frame) 
        load_delete_frame.grid(row=1, column=2, padx=(5,0), pady=(2,5), sticky="w")
        self.btn_load_config = ttk.Button(load_delete_frame, text="Laden", command=self._load_selected_configuration, width=6)
        self.btn_load_config.pack(side="left", padx=(0,2))
        self.btn_delete_config = ttk.Button(load_delete_frame, text="Löschen", command=self._delete_selected_configuration, width=6)
        self.btn_delete_config.pack(side="left")

        # === RECHTE SPALTE ===

        # Kostenzusammenfassung (Oben Rechts)
        summary_frame = ttk.LabelFrame(main_frame, text="Kostenzusammenfassung", padding="10")
        summary_frame.grid(row=0, column=1, padx=5, pady=5, sticky="new") 
        summary_frame.columnconfigure(0, weight=1) 
        ttk.Label(summary_frame, textvariable=self.total_lifetime_cost_var, font=("Helvetica", 11, "bold")).pack(anchor="w", pady=1)
        ttk.Separator(summary_frame, orient='horizontal').pack(fill='x', pady=3, padx=5)
        ttk.Label(summary_frame, textvariable=self.total_financing_var).pack(anchor="w")
        ttk.Label(summary_frame, textvariable=self.total_operation_var).pack(anchor="w")
        ttk.Label(summary_frame, textvariable=self.total_insurance_var).pack(anchor="w")
        ttk.Label(summary_frame, textvariable=self.total_fuel_var).pack(anchor="w")
        ttk.Separator(summary_frame, orient='horizontal').pack(fill='x', pady=3, padx=5)
        ttk.Label(summary_frame, textvariable=self.total_chart_displayed_var, font=("Helvetica", 10, "italic")).pack(anchor="w", pady=1)

        # Eingabeparameter (Direkt unter Kostenzusammenfassung Rechts)
        input_frame = ttk.LabelFrame(main_frame, text="Eingabeparameter", padding="10")
        # Nimmt jetzt die Zeilen 1 und 2 in der rechten Spalte ein.
        input_frame.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky="nsew") 
        input_frame.columnconfigure(1, weight=1)

        row_idx_input = 0
        ttk.Label(input_frame, text="Kaufpreis Auto (€):").grid(row=row_idx_input, column=0, sticky="w", padx=5, pady=2)
        self.entry_purchase_price = ttk.Entry(input_frame, width=20)
        self.entry_purchase_price.grid(row=row_idx_input, column=1, sticky="we", padx=5, pady=2)
        self.entry_purchase_price.insert(0, "25000.0")
        row_idx_input += 1
        
        ttk.Label(input_frame, text="Betriebskosten (€/Monat):").grid(row=row_idx_input, column=0, sticky="w", padx=5, pady=2)
        self.entry_running_costs = ttk.Entry(input_frame)
        self.entry_running_costs.grid(row=row_idx_input, column=1, sticky="we", padx=5, pady=2)
        self.entry_running_costs.insert(0, "150.0")
        row_idx_input += 1

        ttk.Label(input_frame, text="Versicherungskosten (€/Jahr):").grid(row=row_idx_input, column=0, sticky="w", padx=5, pady=2)
        self.entry_insurance_annual_cost = ttk.Entry(input_frame, textvariable=self.insurance_annual_cost_var)
        self.entry_insurance_annual_cost.grid(row=row_idx_input, column=1, sticky="we", padx=5, pady=2)
        row_idx_input += 1

        ttk.Label(input_frame, text="Verbrauch (Liter/100km):").grid(row=row_idx_input, column=0, sticky="w", padx=5, pady=2)
        self.entry_consumption = ttk.Entry(input_frame)
        self.entry_consumption.grid(row=row_idx_input, column=1, sticky="we", padx=5, pady=2)
        self.entry_consumption.insert(0, "7.0")
        row_idx_input += 1

        ttk.Label(input_frame, text="Jahreskilometerleistung (km):").grid(row=row_idx_input, column=0, sticky="w", padx=5, pady=2)
        self.entry_km_per_year = ttk.Entry(input_frame, textvariable=self.km_per_year_var)
        self.entry_km_per_year.grid(row=row_idx_input, column=1, sticky="we", padx=5, pady=2)
        row_idx_input += 1

        ttk.Label(input_frame, text="Kraftstoffpreis (€/Liter):").grid(row=row_idx_input, column=0, sticky="w", padx=5, pady=2)
        self.entry_fuel_price = ttk.Entry(input_frame, textvariable=self.fuel_price_var)
        self.entry_fuel_price.grid(row=row_idx_input, column=1, sticky="we", padx=5, pady=2)
        row_idx_input += 1

        ttk.Label(input_frame, text="Geplante Haltedauer (Jahre):").grid(row=row_idx_input, column=0, sticky="w", padx=5, pady=2)
        self.entry_car_lifetime_years = ttk.Entry(input_frame, textvariable=self.car_lifetime_years_var)
        self.entry_car_lifetime_years.grid(row=row_idx_input, column=1, sticky="we", padx=5, pady=2)
        row_idx_input += 1
        
        ttk.Label(input_frame, text="Preissteigerung p.a. (%):").grid(row=row_idx_input, column=0, sticky="w", padx=5, pady=2)
        self.entry_op_cost_increase = ttk.Entry(input_frame, textvariable=self.operating_cost_increase_var)
        self.entry_op_cost_increase.grid(row=row_idx_input, column=1, sticky="we", padx=5, pady=2)
        tooltip_op_cost_input = tk.Label(input_frame, text="Für Betrieb, Versicherung & Kraftstoff", relief=tk.SUNKEN, bd=1, font=('Helvetica', 7))
        tooltip_op_cost_input.grid(row=row_idx_input, column=2, sticky="w", padx=2)
        row_idx_input += 1
        
        ttk.Label(input_frame, text="Zinsen Finanzierung (eff. % p.a.):").grid(row=row_idx_input, column=0, sticky="w", padx=5, pady=2)
        self.entry_interest_rate = ttk.Entry(input_frame)
        self.entry_interest_rate.grid(row=row_idx_input, column=1, sticky="we", padx=5, pady=2)
        self.entry_interest_rate.insert(0, "3.5")
        row_idx_input += 1
        
        ttk.Label(input_frame, text="Dauer Finanzierung (Jahre):").grid(row=row_idx_input, column=0, sticky="w", padx=5, pady=2)
        self.entry_financing_duration = ttk.Entry(input_frame)
        self.entry_financing_duration.grid(row=row_idx_input, column=1, sticky="we", padx=5, pady=2)
        self.entry_financing_duration.insert(0, "5")
        row_idx_input += 1
        
        ttk.Label(input_frame, text="Schlussrate (€, optional):").grid(row=row_idx_input, column=0, sticky="w", padx=5, pady=2)
        self.entry_balloon_payment = ttk.Entry(input_frame, textvariable=self.balloon_payment_var)
        self.entry_balloon_payment.grid(row=row_idx_input, column=1, sticky="we", padx=5, pady=2)
        row_idx_input += 1
        
        # Der input_frame benötigt eine Zeile, die sich ausdehnen kann, um den Button nach unten zu drücken
        input_frame.rowconfigure(row_idx_input, weight=1) # Diese Zeile wird flexibel

        self.btn_calculate = ttk.Button(input_frame, text="Berechnen & Diagramm aktualisieren", command=self._trigger_calculation)
        # Platziere den Button in einer neuen Zeile am Ende des input_frame
        self.btn_calculate.grid(row=row_idx_input + 1, column=0, columnspan=3, pady=(10,2), sticky="sew") # sticky sew


    # --- Restliche Methoden (_refresh_chart_only, _trigger_calculation, _update_chart, 
    #      _collect_parameters_for_saving, _save_current_configuration, 
    #      _delete_selected_configuration, _load_selected_configuration)
    #      bleiben unverändert von der vorherigen Version. ---
    def _refresh_chart_only(self):
        if hasattr(self, 'calculation_results_buffer') and self.calculation_results_buffer:
            monthly_data = self.calculation_results_buffer.get("monthly_data")
            if monthly_data:
                self._update_chart(monthly_data)

    def _trigger_calculation(self):
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
                self.entry_insurance_annual_cost.state(['invalid']) 
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

            self.calculation_results_buffer = calculator.get_cost_breakdown_for_chart(total_months_for_chart)
            
            monthly_chart_data = self.calculation_results_buffer["monthly_data"]
            total_lifetime_cost = self.calculation_results_buffer["total_lifetime_cost"]
            component_totals = self.calculation_results_buffer["component_totals"]

            def f_curr(val):
                return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"

            self.total_lifetime_cost_var.set(f"Gesamtkosten (Real): {f_curr(total_lifetime_cost)}")
            self.total_financing_var.set(f"Finanzierung (Gesamt): {f_curr(component_totals.get('financing', 0))}")
            self.total_operation_var.set(f"Betrieb (Gesamt): {f_curr(component_totals.get('operation', 0))}")
            self.total_insurance_var.set(f"Versicherung (Gesamt): {f_curr(component_totals.get('insurance', 0))}")
            self.total_fuel_var.set(f"Kraftstoff (Gesamt): {f_curr(component_totals.get('fuel', 0))}")
            
            self._update_chart(monthly_chart_data)
            
        except ValueError as ve: 
            print(f"Eingabefehler in _trigger_calculation: {ve}")
        except Exception as e:
            messagebox.showerror("Unerwarteter Berechnungsfehler", f"Ein Fehler ist aufgetreten: {str(e)}")

    def _update_chart(self, monthly_data_list: list):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not monthly_data_list:
            tk.Label(self.chart_frame, text="Keine Daten zum Anzeigen.").pack(expand=True, fill="both")
            self.total_chart_displayed_var.set("Gesamtkosten (Diagramm): N/A")
            return
        
        displayed_total_sum = 0.0
        if hasattr(self, 'calculation_results_buffer') and \
           self.calculation_results_buffer and \
           'component_totals' in self.calculation_results_buffer:
            
            comp_totals = self.calculation_results_buffer['component_totals']
            if self.show_financing_var.get():
                displayed_total_sum += comp_totals.get('financing', 0)
            if self.show_operation_var.get():
                displayed_total_sum += comp_totals.get('operation', 0)
            if self.show_insurance_var.get():
                displayed_total_sum += comp_totals.get('insurance', 0)
            if self.show_fuel_var.get():
                displayed_total_sum += comp_totals.get('fuel', 0)
        
        def f_curr_simple(val):
            return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"
        self.total_chart_displayed_var.set(f"Gesamtkosten (Diagramm): {f_curr_simple(displayed_total_sum)}")

        try:
            fig = Figure(figsize=(7, 5), dpi=100) 
            ax = fig.add_subplot(111)
            months = [item['month'] for item in monthly_data_list]
            financing_costs = np.array([item.get('financing',0) for item in monthly_data_list]) if self.show_financing_var.get() else np.zeros(len(months))
            operation_costs = np.array([item.get('operation',0) for item in monthly_data_list]) if self.show_operation_var.get() else np.zeros(len(months))
            insurance_costs = np.array([item.get('insurance',0) for item in monthly_data_list]) if self.show_insurance_var.get() else np.zeros(len(months))
            fuel_costs      = np.array([item.get('fuel',0) for item in monthly_data_list])      if self.show_fuel_var.get() else np.zeros(len(months))
            bar_width = 0.8
            current_bottom = np.zeros(len(months))
            legend_handles = []
            if self.show_financing_var.get():
                p1 = ax.bar(months, financing_costs, bar_width, label='Finanzierung', color='skyblue', bottom=current_bottom)
                current_bottom += financing_costs
                legend_handles.append(p1)
            if self.show_operation_var.get():
                p2 = ax.bar(months, operation_costs, bar_width, label='Betriebskosten', color='orange', bottom=current_bottom)
                current_bottom += operation_costs
                legend_handles.append(p2)
            if self.show_insurance_var.get():
                p3 = ax.bar(months, insurance_costs, bar_width, label='Versicherung', color='lightcoral', bottom=current_bottom)
                current_bottom += insurance_costs
                legend_handles.append(p3)
            if self.show_fuel_var.get():
                p4 = ax.bar(months, fuel_costs, bar_width, label='Kraftstoff', color='green', bottom=current_bottom)
                legend_handles.append(p4)
            ax.set_ylabel("Kosten (€)")
            ax.set_title("Monatliche Autokosten (Auswahl)")
            if legend_handles: 
                ax.legend(handles=legend_handles, loc='upper left', fontsize='small')
            num_months_total = len(months)
            year_major_ticks = [m for m in months if (m - 1) % 12 == 0]
            if not year_major_ticks or (1 in months and year_major_ticks[0] != 1) :
                 year_major_ticks = [1] + [yt for yt in year_major_ticks if yt !=1]
            year_major_ticks = sorted(list(set(year_major_ticks)))
            year_labels = [f'Jahr {(m-1)//12 + 1}' for m in year_major_ticks]
            max_year_labels = 12 
            if len(year_labels) > max_year_labels and max_year_labels > 0: 
                step = math.ceil(len(year_labels) / max_year_labels)
                year_major_ticks = year_major_ticks[::step]
                year_labels = year_labels[::step]
            ax.set_xticks(year_major_ticks)
            ax.set_xticklabels(year_labels, rotation=30, ha='right', fontsize='small')
            ax.set_xlabel("Zeitverlauf", fontsize='medium')
            if num_months_total <= 36 and num_months_total > 0 : 
                ax.set_xticks(months, minor=True)
                ax.tick_params(axis='x', which='minor', labelsize='x-small', labelrotation=90)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas.draw()
        except ImportError:
            first_month_data = monthly_data_list[0] if monthly_data_list else {}
            placeholder_text = f"Matplotlib nicht gefunden.\n{len(monthly_data_list)} Monate berechnet.\nErster Monat Gesamt (Basis): {first_month_data.get('total',0):.2f}€\n(Details: F:{first_month_data.get('financing',0):.2f}, B:{first_month_data.get('operation',0):.2f}, V:{first_month_data.get('insurance',0):.2f}, K:{first_month_data.get('fuel',0):.2f})"
            tk.Label(self.chart_frame, text=placeholder_text, justify=tk.LEFT).pack(expand=True, fill="both")
        except Exception as e:
            tk.Label(self.chart_frame, text=f"Fehler beim Erstellen des Diagramms: {e}").pack(expand=True, fill="both")

    def _collect_parameters_for_saving(self) -> dict:
        params_to_save = {
            "car_purchase_price": self._get_float_from_entry(self.entry_purchase_price, field_name="Kaufpreis"),
            "car_running_costs_monthly": self._get_float_from_entry(self.entry_running_costs, field_name="Betriebskosten"),
            "car_consumption_per_100km": self._get_float_from_entry(self.entry_consumption, field_name="Verbrauch"),
            "financing_interest_rate_percent": self._get_float_from_entry(self.entry_interest_rate, field_name="Zinssatz"),
            "financing_duration_years": self._get_int_from_entry(self.entry_financing_duration, field_name="Finanzierungsdauer"),
            "financing_balloon_payment": self.balloon_payment_var.get(),
            "insurance_annual_cost": self.insurance_annual_cost_var.get(),
            "usage_km_per_year": self.km_per_year_var.get(),
            "usage_fuel_price_per_liter": self.fuel_price_var.get(),
            "usage_car_lifetime_years": self.car_lifetime_years_var.get(),
            "general_operating_cost_increase_percent": self.operating_cost_increase_var.get(),
        }
        return params_to_save

    def _save_current_configuration(self):
        config_name = self.config_name_var.get().strip()
        if not config_name:
            messagebox.showerror("Fehler beim Speichern", "Bitte einen Namen für die Konfiguration eingeben.")
            self.entry_config_name.focus_set()
            return
        try:
            current_params = self._collect_parameters_for_saving()
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
            if config_name in self.saved_configs_list:
                self.combo_saved_configs.set(config_name)
        except ValueError:
             messagebox.showwarning("Speichern abgebrochen", 
                                    "Bitte korrigieren Sie die Eingabefehler (rot markiert), bevor Sie speichern.")
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", f"Ein unerwarteter Fehler ist aufgetreten:\n{str(e)}")

    def _delete_selected_configuration(self):
        selected_name = self.combo_saved_configs.get()
        if not selected_name:
            messagebox.showinfo("Löschen", "Bitte wählen Sie zuerst eine zu löschende Konfiguration aus der Liste aus.")
            return

        if messagebox.askyesno("Löschen bestätigen", 
                               f"Sind Sie sicher, dass Sie die Konfiguration '{selected_name}' unwiderruflich löschen möchten?"):
            all_configs = self._read_data_file()
            if selected_name in all_configs:
                del all_configs[selected_name]
                self._write_data_file(all_configs)
                messagebox.showinfo("Gelöscht", f"Konfiguration '{selected_name}' wurde gelöscht.")
                self.config_name_var.set("") 
            else:
                messagebox.showwarning("Fehler", f"Konfiguration '{selected_name}' wurde nicht in der Speicherdatei gefunden.")
            
            self._update_saved_configs_dropdown()


    def _load_selected_configuration(self):
        selected_name = self.combo_saved_configs.get()
        if not selected_name:
            messagebox.showinfo("Laden", "Bitte wählen Sie eine Konfiguration aus der Liste aus.")
            return
        all_configs = self._read_data_file()
        loaded_params = all_configs.get(selected_name)
        if not loaded_params:
            messagebox.showerror("Fehler beim Laden", f"Konfiguration '{selected_name}' nicht in der Datei gefunden.")
            self._update_saved_configs_dropdown()
            return
        try:
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
            self.config_name_var.set(selected_name)
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
            self._trigger_calculation()
        except Exception as e:
            messagebox.showerror("Fehler beim Laden der Parameter", f"Ein unerwarteter Fehler ist aufgetreten:\n{str(e)}")
