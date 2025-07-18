import pandas as pd

URL_CONFIGURACION = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8E3cr73eOHXX-unVuxlA0L3jydzA4hCMP1ZNFTJBhGAVmLo3OpulCjDyhxd7vby7JvBTXUMF66wIS/pub?gid=2133313737&single=true&output=csv"

def cargar_configuracion():
    try:
        df = pd.read_csv(URL_CONFIGURACION)
        df = df.fillna('')  # Reemplazar NaN con cadena vacía
        config = {fila['Clave']: fila['Valor'] for _, fila in df.iterrows()}
        return {
            'NombreNegocio': config.get('NombreNegocio', 'Mi Negocio'),
            'CorreoNotificaciones': config.get('CorreoNotificaciones', ''),
            'Moneda': config.get('Moneda', '₡'),
            'color': config.get('ColorPrincipal', '#0d6efd'),
            'color_fondo': config.get('ColorFondo', '#ffffff'),
            'logo': config.get('LogoURL', ''),
            'URLScript': config.get('URLScript', ''),
            'URLScriptProveedores': config.get('URLScriptProveedores', ''),
            'URLScriptProductos': config.get('URLScriptProductos', ''),
            'URLScriptConfig': config.get('URLScriptConfig', ''),
            'URLProveedores': config.get('URLProveedores', ''),
            'URLProductos': config.get('URLProductos', ''),
        }
    except Exception as e:
        print("Error cargando configuración:", e)
        return {}
