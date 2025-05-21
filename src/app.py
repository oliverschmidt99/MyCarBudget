# src/app.py
import tkinter as tk
from .gui import CarCostGUI

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.gui = CarCostGUI(self.root)

    def run(self):
        """Startet die Hauptschleife der grafischen Benutzeroberfläche."""
        self.root.mainloop()