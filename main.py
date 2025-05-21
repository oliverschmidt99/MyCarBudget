# cost_car_calc/main.py
import sys
import os

# Fügt das Projekt-Stammverzeichnis (cost_car_calc) zum Python-Pfad hinzu.
# os.path.dirname(__file__) ist /home/oliver/Dokumente/git/cost_car_calc
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Importiere App als Teil des 'src'-Pakets
from src.app import App

if __name__ == "__main__":
    application = App()
    application.run()