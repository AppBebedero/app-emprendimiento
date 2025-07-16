from flask import Flask, render_template, request, jsonify
from config_loader import cargar_configuracion
import csv
import requests
import os
import pandas as pd

app = Flask(__name__)

# --- Configuración de carpetas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# --- Funciones auxiliares ---
def leer_csv_config(url):
    try:
        df = pd.read_csv(url)
        return df.fillna('').to_dict(orient='records')
    except Exception as e:
        print(f"❌ Error leyendo CSV desde {url}:", e)
        return []

def leer_lista_desde_csv(nombre_archivo):
    try:
        ruta = os.path.join(DATA_DIR, nombre_archivo)
        with open(ruta, newline='', encoding='utf-8') as archivo:
            return [fila[0] for fila in csv.reader(archivo) if fila and fila[0] != '']
    except FileNotFoundError:
        print(f"❌ Archivo {nombre_archivo} no encontrado en /data.")
        return []

def enviar_a_script(url, datos):
    try:
        respuesta = requests.post(url, data=datos)
        print("📥 Respuesta del script:", respuesta.text)
        return respuesta.status_code == 200
    except Exception as e:
        print("❌ Error al enviar datos al script:", e)
        return False

# --- Rutas principales ---

@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()
    if request.method == 'POST':
        datos = {
            'Fecha': request.form.get('Fecha'),
            'N_Documento': request.form.get('N_Documento'),
            'Proveedor': request.form.get('Proveedor'),
            'Producto': request.form.get('Producto'),
            'Cantidad': request.form.get('Cantidad'),
            'PrecioUnitario': request.form.get('PrecioUnitario'),
            'Moneda': request.form.get('Moneda'),
            'Forma_Pago': request.form.get('Forma_Pago'),
            'Observaciones': request.form.get('Observaciones')
        }
        exito = enviar_a_script(config.get('URLScript'), datos)
        if exito:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Error al guardar'}), 500

    formas_pago = ['Efectivo', 'SINPE', 'Tarjeta Cr.']
    return render_template('compras.html', formas_pago=formas_pago)

@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    config = cargar_configuracion()
    datos = {k: request.form[k] for k in request.form}
    if not datos.get('nombre') or not datos.get('tipo_negocio'):
        return jsonify({'error': 'Nombre y Tipo de Negocio son obligatorios'}), 400

    exito = enviar_a_script(config.get('URLScriptProveedores'), datos)
    if exito:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Error al guardar proveedor'}), 500

@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    config = cargar_configuracion()
    datos = {k: request.form[k] for k in request.form}
    if not datos.get('nombre') or not datos.get('proveedor') or not datos.get('categoria') or not datos.get('unidad'):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    exito = enviar_a_script(config.get('URLScriptProductos'), datos)
    if exito:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Error al guardar producto'}), 500

@app.route('/datos_formulario')
def datos_formulario():
    config = cargar_configuracion()

    proveedores = leer_csv_config(config.get('URLProveedores'))
    productos = leer_csv_config(config.get('URLProductos'))
    tipos_negocio = leer_lista_desde_csv('tipos_negocio.csv')
    categorias = leer_lista_desde_csv('categorias.csv')
    unidades = leer_lista_desde_csv('unidades.csv')

    return jsonify({
        'proveedores': proveedores,
        'productos': productos,
        'tipos_negocio': tipos_negocio,
        'categorias': categorias,
        'unidades': unidades
    })

# --- Ejecución local (opcional) ---
if __name__ == '__main__':
    app.run(debug=True)
