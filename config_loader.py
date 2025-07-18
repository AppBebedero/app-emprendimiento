import csv
import requests
from io import StringIO

def cargar_configuracion():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTIKxEMh8W7RRoqpqkaCF4ZIMDLFc-Nf7U9kLuKXx2pWqQeEGqljcTgF__mqO0lgGbMGrps-t90WrOr/pub?gid=2133313737&single=true&output=csv"

    try:
        response = requests.get(url)
        response.raise_for_status()
        contenido = response.content.decode('utf-8')
        lector = csv.reader(StringIO(contenido))
        datos = list(lector)

        config = {}
        for fila in datos:
            if len(fila) >= 2:
                clave = fila[0].strip()
                valor = fila[1].strip()
                config[clave] = valor
        return config

    except Exception as e:
        print("Error cargando configuración:", e)
        return {}
