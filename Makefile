# Makefile für den Autokostenrechner

# Variablen
PYTHON ?= python3
VENV_DIR = .venv
# Pfad zu Python und Pip innerhalb der venv, abhängig vom Betriebssystem
ifeq ($(OS),Windows_NT)
    PIP = $(VENV_DIR)/Scripts/pip
    PYTHON_VENV = $(VENV_DIR)/Scripts/python
    ACTIVATE_SCRIPT = $(VENV_DIR)/Scripts/activate
else
    PIP = $(VENV_DIR)/bin/pip
    PYTHON_VENV = $(VENV_DIR)/bin/python
    ACTIVATE_SCRIPT = $(VENV_DIR)/bin/activate
endif

# Standardziel: Programm starten
run: $(PYTHON_VENV) main.py
	@echo "Starte Autokostenrechner..."
	@$(PYTHON_VENV) main.py

# Virtuelle Umgebung erstellen
$(VENV_DIR):
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Erstelle virtuelle Umgebung in $(VENV_DIR)..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "Virtuelle Umgebung erstellt."; \
	else \
		echo "Virtuelle Umgebung $(VENV_DIR) existiert bereits."; \
	fi

# Abhängigkeiten installieren (setzt voraus, dass venv existiert)
install_deps: $(VENV_DIR) requirements.txt
	@echo "Installiere Abhängigkeiten aus requirements.txt...";
	@$(PIP) install -r requirements.txt
	@echo "Abhängigkeiten installiert."
	@# Erstelle oder aktualisiere einen Zeitstempel-Dummy, um die erfolgreiche Installation zu markieren
	@# Dies hilft 'make', zu wissen, wann die Abhängigkeiten aktuell sind.
	@touch $(VENV_DIR)/.deps_installed 

# Alias für die komplette Einrichtung: venv erstellen und Abhängigkeiten installieren
venv: $(VENV_DIR)/.deps_installed

# Das Ziel .deps_installed hängt vom activate Script und install_deps ab
# Dies ist ein Dummy-Ziel, um die Installation der Abhängigkeiten zu verfolgen
$(VENV_DIR)/.deps_installed: $(ACTIVATE_SCRIPT) install_deps

# Das Activate-Skript hängt von der Erstellung der venv ab
$(ACTIVATE_SCRIPT): $(VENV_DIR)

# Programm direkt mit dem System-Python starten (falls venv nicht gewünscht)
run_system:
	@echo "Starte Autokostenrechner mit System-Python..."
	@$(PYTHON) main.py

# Aufräumen: Virtuelle Umgebung und __pycache__ entfernen
clean:
	@echo "Entferne virtuelle Umgebung und __pycache__ Verzeichnisse..."
	@rm -rf $(VENV_DIR)
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Bereinigung abgeschlossen."

# Hilfe anzeigen
help:
	@echo "Verfügbare Befehle:"
	@echo "  make venv         - Erstellt die virtuelle Umgebung und installiert Abhängigkeiten."
	@echo "  make run          - Startet das Programm (verwendet die virtuelle Umgebung, ruft ggf. 'make venv' auf)."
	@echo "  make install_deps - Installiert/Aktualisiert Abhängigkeiten (setzt existierende venv voraus)."
	@echo "  make run_system   - Startet das Programm mit dem System-Python."
	@echo "  make clean        - Entfernt die virtuelle Umgebung und Cache-Dateien."
	@echo "  make help         - Zeigt diese Hilfe an."

.PHONY: run venv install_deps run_system clean help