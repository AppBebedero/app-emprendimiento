import requests
import csv
from io import StringIO
from config_loader import cargar_configuracion

def lista_proveedores():
    config = cargar_configuracion()
    url = config.get('URLProveedores')
    resp = requests.get(url)
    resp.raise_for_status()
    reader = csv.DictReader(StringIO(resp.text))
    return list(reader)

def guardar_proveedor(datos):
    config = cargar_configuracion()
    url = config.get('URLScriptProveedores')
    resp = requests.post(url, json=datos)
    resp.raise_for_status()
    return resp.json()
