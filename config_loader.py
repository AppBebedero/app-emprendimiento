import csv
import requests

def cargar_configuracion():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS7iAAwPLN9UAFYtWoNYb28RD0gCIjKLIVRaTfWCTMeS83phMlZC_K4NQm1NzFiVQ/pub?gid=2133313737&single=true&output=csv"
    config = {}

    try:
        response = requests.get(url)
        response.raise_for_status()
        contenido = response.content.decode("utf-8").splitlines()
        lector = csv.DictReader(contenido)
        for fila in lector:
            clave = fila.get("Clave", "").strip()
            valor = fila.get("Valor", "").strip()
            if clave:
                config[clave] = valor

        # Campos con nombre más fácil para usar en HTML
        config["color_principal"] = config.get("ColorPrincipal", "#0d6efd")
        config["color_fondo"] = config.get("ColorFondo", "#ffffff")
        config["logo_url"] = config.get("LogoURL", "")
        config["nombre_negocio"] = config.get("NombreNegocio", "Mi Negocio")
        config["logo_exists"] = bool(config["logo_url"])

    except Exception as e:
        print("Error cargando configuración:", e)

    return config
