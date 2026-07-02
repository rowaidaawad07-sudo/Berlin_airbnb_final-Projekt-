README – Berlin Airbnb Datenanalyse & Preisvorhersage
1. Projektübersicht
Dieses Projekt analysiert Airbnb‑Daten aus Berlin und erstellt ein Preisvorhersage‑Modell. Es umfasst:

Datenbereinigung und -aufbereitung

Explorative Datenanalyse (EDA)

Statistische Analysen

Maschinelles Lernen (Regression & Klassifikation)

Automatisiertes E‑Mail‑System für Anfragen

Die gesamte Pipeline ist modular aufgebaut und kann entweder manuell oder vollautomatisch ausgeführt werden.

2. Beschreibung der Hauptdateien
2.1 Datenbereinigung & -aufbereitung
data_cleaning.py (unter src/)
Lädt die Rohdaten, bereinigt sie (fehlende Werte, Preisformatierung, Duplikate) und speichert die bereinigte CSV.

import_raw_data.py
Importiert die Rohdaten in eine PostgreSQL‑Tabelle (airbnb_raw) über SQLAlchemy.

relational_model.py
Erstellt aus der Rohdaten‑Tabelle separate relationale Tabellen für Hosts, Listings, Bewertungen und Bewertungskennzahlen.

2.2 Explorative und statistische Analyse
eda_analysis.py
Erzeugt verschiedene Diagramme (Preisverteilung, Korrelationsmatrix, Boxplots usw.) und einen zusammenfassenden Bericht (eda_report.txt) im Ordner reports/.

statistical_analysis.py
Führt Korrelations‑, ANOVA‑ und Regressionsanalysen durch, berechnet den VIF und erzeugt Diagnosegrafiken (Residuen, Vorhersage vs. tatsächlicher Preis).

2.3 Preprocessing (Feature‑Engineering)
Preprocessing.ipynb (unter src/notebooks)
Jupyter‑Notebook, das die bereinigten Daten für das maschinelle Lernen aufbereitet:

Entfernen irrelevanter Spalten

Behandlung von Ausreißern beim Preis

One‑Hot‑Encodierung kategorialer Merkmale

Speichern des finalen Datensatzes (berlin_airbnb_regression.csv)

2.4 Maschinelles Lernen
Machine_learning.ipynb (unter src/ notebooks)
Trainiert und vergleicht vier Modelle:

Lineare Regression

Random Forest

XGBoost

Neuronales Netz (FNN)

klassifikation 

Speichert das beste Modell (Random Forest) und die benötigten Metadaten (training_metadata.json, model_columns.pkl).

ml_functions.py ( unter src/ml)
Enthält Hilfsfunktionen zur Extraktion von Features aus E‑Mail‑Texten (Regex + Ollama), zur Erstellung von KI‑Antworten und zur Preisvorhersage.

edit_training.py ( unter src/ml)
Korrigiert Kodierungsfehler in der training_metadata.json (z. B. Umlaute).

3.5 Automatisierung
email_system.py ( unter src/automation)
Überwacht ein E‑Mail‑Postfach auf ungelesene Anfragen, extrahiert mit ml_functions.py die relevanten Merkmale, sagt den Preis voraus, speichert die Anfrage in die Datenbank und sendet eine automatische Antwort.

3.6 Orchestrierung
main.py
Startet die gesamte Pipeline: Datenbereinigung → relationale Tabellen.

run_all.py
Führt nacheinander data_cleaning.py, eda_analysis.py, statistical_analysis.py, import_raw_data.py und relational_model.py aus.

config.py
Zentrale Konfiguration für Pfade und die Datenbank‑URL.

database.py
Stellt die SQLAlchemy‑Engine mit der Datenbankverbindung bereit.

3. Einrichtung & Installation
Repository klonen

bash
git clone <repository-url>
cd berlin_airbnb_final
Virtuelle Umgebung erstellen und aktivieren

bash
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows
Abhängigkeiten installieren

bash
pip install -r requirements.txt
Die wichtigsten Pakete: pandas, numpy, scikit‑learn, xgboost, matplotlib, seaborn, sqlalchemy, psycopg2, imaplib, smtplib, langdetect, requests, joblib.

Datenbank einrichten

PostgreSQL installieren und starten.

Datenbank berlin_airbnb_final erstellen.

Zugangsdaten in config.py anpassen (DATABASE_URL).

Rohdaten
Die Datei berlin_airbnb_sample.csv muss im Ordner data/raw/ liegen.

Ollama (für KI‑Antworten)

Ollama installieren und das Modell llama3.2:1b pullen:

bash
ollama pull llama3.2:1b
Der Service muss lokal auf Port 11434 laufen.

E‑Mail‑Konto (für das Automatisierungssystem)

In email_system.py die Variablen EMAIL_USER und EMAIL_PASS (App‑Passwort bei Gmail) setzen.

IMAP und SMTP müssen aktiviert sein.

4. Ausführung
4.1 Schritt‑für‑Schritt (empfohlen für Entwicklung)
Datenbereinigung

bash
python src/cleaning/clean_data.py
Erzeugt berlin_airbnb_cleaned.csv in data/processed/.

Explorative Datenanalyse

bash
python src/analysis/eda_analysis.py
Erstellt Berichte und Diagramme in reports/.

Statistische Analyse

bash
python src/analysis/statistical_analysis.py
Erzeugt den statistischen Bericht.

Preprocessing
Führen Sie das Notebook src/ml/Preprocessing.ipynb aus. Es erstellt berlin_airbnb_regression.csv.

Modelltraining
Führen Sie src/ml/Machine_learning.ipynb aus. Es speichert das Random‑Forest‑Modell und die Metadaten.

Relationale Tabellen (optional)

bash
python relational_model.py
(Benötigt eine laufende PostgreSQL‑Datenbank.)

4.2 Automatische Pipeline
main.py

bash
python main.py
Führt nur clean_data.py und create_tables.py aus.

run_all.py

bash
python run_all.py
Führt alle oben genannten Skripte (außer Notebooks) nacheinander aus.

4.3 E‑Mail‑Automatisierung starten
bash
python src/automation/email_system.py
Das System prüft alle 60 Sekunden das Postfach auf neue ungelesene E‑Mails.

5. Abhängigkeiten
Die vollständige Liste befindet sich in requirements.txt. Wichtige Pakete:

Datenverarbeitung: pandas, numpy

Visualisierung: matplotlib, seaborn

ML: scikit‑learn, xgboost

Datenbank: sqlalchemy, psycopg2

E‑Mail: imaplib, smtplib (in Python enthalten)

Weitere: langdetect, requests, joblib

6. Wichtige Hinweise
Datenbank: Die Skripte import_raw_data.py und relational_model.py setzen eine laufende PostgreSQL‑Instanz mit der richtigen Datenbank voraus.

Encoding: Achten Sie auf UTF‑8, insbesondere bei deutschen Umlauten. Das Skript edit_training.py korrigiert bekannte Kodierungsfehler.

Modell: Das trainierte Modell wird als rf_model.pkl gespeichert. Stellen Sie sicher, dass die Feature‑Reihenfolge beim Vorhersagen exakt mit den gespeicherten Spalten (model_columns.pkl) übereinstimmt.

E‑Mail‑System: Verwenden Sie für #Gmail ein App‑Passwort, da die Zwei‑Faktor‑Authentifizierung das normale Passwort blockiert.

Ollama: Der Dienst muss vor dem Start von email_system.py laufen.

## Organisation und Nachverfolgung der Projektaufgaben mittels Trello (Task-Management, Sprint-Planung).

### Zusätzliche Angaben zur Projektentwicklung (Ergänzung)
Im Rahmen der Projektarbeit wurden die folgenden Aufgaben von den genannten Personen übernommen:

Vorbereitung der Rohdaten (Datenbereinigung, Imputation fehlender Werte, Formatierung):
Rowaida and Blerina

Erstellung der Datenbank-Codes (Tabellenentwurf, SQL-Schemata, Anbindung an PostgreSQL):
Rowaida and Blerina

Explorative Datenanalyse und statistische Auswertung (EDA, Korrelationsanalysen, ANOVA, Regressionsdiagnostik):
Rowaida

Training der Machine-Learning-Modelle (Preprocessing, Modellvergleich, Hyperparameter-Optimierung, Speicherung des finalen Modells):
Rowaida and Blerina 
Rowaida FNN

Entwicklung der Automatisierung (E-Mail-System, Integration von Ollama, automatisierte Antwortgenerierung):
Rowaida

Erstellung der PowerPoint-Präsentation für die erste Version (Projektvorstellung, erste Ergebnisse, Visualisierungen):
Rowaida

Erstellung der endgültigen Version (Überarbeitung der Dokumentation, finale Code-Bereinigung, Abschlussbericht):
Rowaida

Abschließende Weiterentwicklung und Gesamtkoordination des Projekts (Qualitätssicherung, Integration aller Module, Deployment-Vorbereitung):
Rowaida