# Autokostenrechner 🚗💨

Ein Programm zur detaillierten Berechnung und Visualisierung der Kosten eines Autos über dessen gesamte Lebensdauer. Es bietet eine grafische Benutzeroberfläche zur Parametereingabe, Speicherung von Konfigurationen und Darstellung der monatlichen Kosten als gestapeltes Balkendiagramm.

## Funktionen ✨

- **Detaillierte Kostenerfassung:** Berücksichtigt Kaufpreis, Betriebskosten, Verbrauch, Versicherung und Finanzierungsdetails (Zinsen, Laufzeit, optionale Schlussrate).
- **Preissteigerung:** Optionale jährliche Preissteigerung für laufende Kosten.
- **Interaktives Diagramm:**
  - Stellt die monatlichen Kosten (Finanzierung, Betrieb, Versicherung, Kraftstoff) als gestapelte Balken dar.
  - Die X-Achse zeigt Jahre für eine bessere Übersicht über lange Zeiträume.
  - Einzelne Kostenkategorien können im Diagramm ein- und ausgeblendet werden.
  - Die Schlussrate wird in der Gesamtkostenberechnung berücksichtigt, aber zur besseren Lesbarkeit nicht direkt im monatlichen Finanzierungsbalken verzerrt dargestellt.
- **Kostenzusammenfassung:**
  - Anzeige der tatsächlichen Gesamtkosten über die Haltedauer.
  - Anzeige der summierten Gesamtkosten für jede einzelne Hauptkategorie (Finanzierung, Betrieb, Versicherung, Kraftstoff).
  - Anzeige der Summe der Kosten, die aktuell im Diagramm durch die ausgewählten Kategorien dargestellt werden.
- **Konfigurationsmanagement:**
  - Speichern beliebig vieler Fahrzeugkonfigurationen unter einem benutzerdefinierten Namen in einer lokalen `data.json`-Datei.
  - Laden gespeicherter Konfigurationen aus einer Dropdown-Liste.
  - Löschen nicht mehr benötigter Konfigurationen mit Bestätigungsdialog.
- **Grafische Benutzeroberfläche (GUI):** Intuitive Eingabe aller Parameter und direkte Visualisierung der Ergebnisse.

## Installation ⚙️

Das Programm ist in Python geschrieben und verwendet die Standardbibliothek Tkinter für die GUI sowie Matplotlib und NumPy für die Diagrammdarstellung.

### Voraussetzungen

* **Python 3:** Stelle sicher, dass Python 3 (Version 3.7 oder neuer empfohlen) auf deinem System installiert ist. Du kannst Python von [python.org](https://www.python.org/) herunterladen.
* **pip:** Der Python-Paketmanager wird benötigt, um Abhängigkeiten zu installieren. Er ist normalerweise bei aktuellen Python-Installationen enthalten.
* **Git:** (Optional) Um das Repository zu klonen.
* **Make:** (Optional, für Linux/macOS) Das `make`-Build-Tool wird benötigt, um die `Makefile` zu verwenden. Es ist auf den meisten Linux-Distributionen und macOS standardmäßig installiert.

### Schritte

1.  **Repository klonen (optional):**
    ```bash
    git clone https://github.com/oliverschmidt99/cost_car_calc/tree/main
    cd cost_car_calc
    ```
    Alternativ kannst du die Projektdateien als ZIP herunterladen und entpacken. Stelle sicher, dass sich die Dateien `Makefile` und `requirements.txt` im Hauptverzeichnis befinden.

2.  **Installation der Abhängigkeiten:**

    * **Mit `Makefile` (empfohlen für Linux/macOS):**
        Navigiere in das Hauptverzeichnis des Projekts (`cost_car_calc`) und führe folgenden Befehl im Terminal aus:
        ```bash
        make venv
        ```
        Dieser Befehl wird:
        1.  Eine virtuelle Python-Umgebung im Ordner `.venv` erstellen (falls noch nicht vorhanden).
        2.  Die virtuelle Umgebung aktivieren.
        3.  Alle notwendigen Pakete (`matplotlib`, `numpy`) aus der `requirements.txt`-Datei in dieser Umgebung installieren.

        Vor jeder weiteren Nutzung des Programms solltest du die virtuelle Umgebung aktivieren:
        ```bash
        source .venv/bin/activate
        ```

    * **Manuelle Installation (Windows oder falls `make` nicht verfügbar/gewünscht):**
        Navigiere in das Hauptverzeichnis des Projekts (`cost_car_calc`). Es wird dringend empfohlen, eine virtuelle Umgebung zu verwenden:
        ```bash
        # 1. Virtuelle Umgebung erstellen (einmalig)
        python -m venv .venv

        # 2. Virtuelle Umgebung aktivieren:
        #    Windows (PowerShell):
        #    .\.venv\Scripts\Activate.ps1
        #    Windows (CMD):
        #    .\.venv\Scripts\activate.bat
        #    Linux/macOS (falls make nicht verwendet wird):
        #    source .venv/bin/activate

        # 3. Abhängigkeiten installieren (innerhalb der aktiven venv):
        pip install -r requirements.txt 
        ```
        Oder direkt (weniger empfohlen als venv):
        ```bash
        pip  install --break-system-packages matplotlib numpy
        ```
        Stelle sicher, dass `pip` auf die korrekte Python 3-Installation verweist (ggf. `pip3` verwenden).

3.  **Programm starten:**

    * **Mit `Makefile` (nachdem `make venv` ausgeführt wurde und die venv aktiv ist, oder direkt):**
        ```bash
        make run
        ```
        Dieser Befehl startet das Programm unter Verwendung der virtuellen Umgebung.

    * **Manuell (innerhalb der aktivierten virtuellen Umgebung):**
        ```bash
        python main.py
        ```
    * **Manuell (ohne virtuelle Umgebung, falls so installiert):**
        ```bash
        python main.py 
        ```
        (Unter Linux/macOS eventuell `python3 main.py` verwenden).

### Hinweise für spezifische Betriebssysteme

* **Linux:** Stelle sicher, dass `tkinter` und `python3-venv` installiert sind. Bei vielen Distributionen sind sie standardmäßig enthalten oder leicht nachzuinstallieren (z.B. `sudo apt-get install python3-tk python3-venv` für Debian/Ubuntu).
* **macOS:** Python, das mit macOS geliefert wird, könnte veraltet sein. Es wird empfohlen, eine aktuelle Version von python.org oder über Paketmanager wie Homebrew zu installieren. Tkinter sollte mit den offiziellen Python-Installationen für macOS funktionieren. `make` ist normalerweise über die Xcode Command Line Tools verfügbar.
* **Windows:** Für die manuelle Installation enthalten die Python-Installationen von python.org normalerweise Tkinter und pip. Die `Makefile` ist unter Windows nicht direkt ohne zusätzliche Tools (wie "GNU Make for Windows" oder WSL) nutzbar; hier ist die manuelle Installation der empfohlene Weg.

## Bedienung 👨‍💻

1.  Gib im Bereich "Eingabeparameter" alle relevanten Daten für das Fahrzeug, die Nutzung und die Finanzierung ein.
2.  Klicke auf "Berechnen & Diagramm aktualisieren".
3.  Die Ergebnisse werden in der "Kostenzusammenfassung" und im Diagramm angezeigt.
4.  Über die "Diagramm Optionen" kannst du einzelne Kostenblöcke im Diagramm ein-/ausblenden.
5.  Im Bereich "Konfigurationen Verwalten":
    - Gib einen Namen ein und klicke auf "Speichern", um die aktuelle Eingabe zu sichern.
    - Wähle eine gespeicherte Konfiguration aus der Liste aus und klicke auf "Laden", um sie zu verwenden.
    - Wähle eine Konfiguration aus und klicke auf "Löschen", um sie (nach Bestätigung) zu entfernen.

Viel Erfolg bei der Kostenkalkulation!
