import pandas as pd

def cargar_configuracion():
    url_csv = 'https://docs.google.com/spreadsheets/d/e/tu_url_de_csv/pub?gid=0&single=true&output=csv'
    df = pd.read_csv(url_csv)
    config = {}

    for _, fila in df.iterrows():
        clave = str(fila['Clave']).strip()
        valor = str(fila['Valor']).strip()
        config[clave] = valor

    return config
