import requests
import csv
from io import StringIO

def cargar_configuracion():
    """Lee la hoja Configuración desde Google Sheets y devuelve un diccionario."""
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8E3cr73eOHXX-unVuxlA0L3jydzA4hCMP1ZNFTJBhGAVmLo3OpulCjDyhxd7vby7JvBTXUMF66wIS/pub?gid=2133313737&single=true&output=csv"
    resp = requests.get(SHEET_URL)
    resp.raise_for_status()
    reader = csv.DictReader(StringIO(resp.text))
    return { row['Clave']: row['Valor'] for row in reader }
