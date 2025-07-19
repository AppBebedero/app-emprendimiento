import requests
import csv
from io import StringIO

def cargar_configuracion():
    """Lee la hoja Configuración desde Google Sheets y devuelve un diccionario."""
    SHEET_URL = "TU_URL_CONFIG_CSV"
    resp = requests.get(SHEET_URL)
    resp.raise_for_status()
    reader = csv.DictReader(StringIO(resp.text))
    # Asume columnas: Clave, Valor
    return { row['Clave']: row['Valor'] for row in reader }
