from flask import Flask, render_template, request, jsonify
import pandas as pd
import requests
import os
import csv
from config_loader import cargar_configuracion

app = Flask(__name__)

# Crear carpeta /data si no existe
os.makedirs("data", exist_ok=True)

# Función para leer CSV locales simples

def leer_lista_desde_csv(ruta):
    try:
        with open(ruta, newline='', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

# Ruta de inicio
@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

# Ruta para vista de compras
@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()
    if request.method == 'POST':
        try:
            datos = {
                'Fecha': request.form['Fecha'],
                'N_Documento': request.form['N_Documento'],
                'Proveedor': request.form['Proveedor'],
                'Producto': request.form['Producto'],
                'Cantidad': request.form['Cantidad'],
                'PrecioUnitario': request.form['PrecioUnitario'],
                'Moneda': request.form['Moneda'],
                'Forma_Pago': request.form['Forma_Pago'],
                'Observaciones': request.form['Observaciones']
            }
            r = requests.post(config['URLScript'], data=datos)
            return ('', 204) if r.status_code == 200 else (r.text, 500)
        except Exception as e:
            return str(e), 500

    formas_pago = ['Efectivo', 'SINPE', 'Tarjeta Cr.', 'Transferencia']
    return render_template('compras.html', formas_pago=formas_pago)

# Ruta para recibir datos para listas desplegables
@app.route('/datos_formulario')
def datos_formulario():
    config = cargar_configuracion()

    def leer_csv_remoto(url):
        try:
            df = pd.read_csv(url)
            return df.to_dict(orient='records')
        except:
            return []

    proveedores = leer_csv_remoto(config.get('URLProveedores', ''))
    productos = leer_csv_remoto(config.get('URLProductos', ''))
    tipos_negocio = leer_lista_desde_csv('data/tipos_negocio.csv')
    categorias = leer_lista_desde_csv('data/categorias.csv')
    unidades = leer_lista_desde_csv('data/unidades.csv')

    return jsonify({
        'proveedores': proveedores,
        'productos': productos,
        'tipos_negocio': tipos_negocio,
        'categorias': categorias,
        'unidades': unidades
    })

# Ruta para nuevo proveedor
@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    config = cargar_configuracion()
    try:
        datos = {
            'Nombre': request.form['nombre'],
            'Teléfono': request.form['telefono'],
            'Email': request.form['email'],
            'Contacto': request.form['contacto'],
            'Celular': request.form['celular'],
            'Tipo de Negocio': request.form['tipo_negocio'],
            'Observaciones': request.form['observaciones']
        }
        r = requests.post(config['URLScriptProveedores'], data=datos)
        if r.status_code == 200:
            return jsonify({'ok': True})
        else:
            return jsonify({'error': r.text}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para nuevo producto
@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    config = cargar_configuracion()
    try:
        datos = {
            'Nombre': request.form['nombre'],
            'Proveedor': request.form['proveedor'],
            'Categoría': request.form['categoria'],
            'Unidad': request.form['unidad'],
            'Observaciones': request.form['observaciones']
        }
        r = requests.post(config['URLScriptProductos'], data=datos)
        if r.status_code == 200:
            return jsonify({'ok': True})
        else:
            return jsonify({'error': r.text}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
