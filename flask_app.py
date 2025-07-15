from flask import Flask, render_template, request, jsonify
from config_loader import cargar_configuracion
import csv
import os
import requests
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Ruta inicio
@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

# Ruta formulario de compras
@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()
    if request.method == 'POST':
        url_script = config.get("URLScript", "")
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
        try:
            response = requests.post(url_script, data=datos)
            if response.status_code == 200:
                return '', 200
            else:
                return response.text, 500
        except Exception as e:
            return str(e), 500

    formas_pago = ["Efectivo", "SINPE", "Tarjeta Cr."]
    return render_template('compras.html', formas_pago=formas_pago)

# Ruta para cargar datos desplegables
@app.route('/datos_formulario')
def datos_formulario():
    config = cargar_configuracion()

    def leer_csv(url):
        try:
            response = requests.get(url)
            response.encoding = 'utf-8'
            return list(csv.DictReader(response.text.splitlines()))
        except:
            return []

    proveedores = leer_csv(config.get('URLProveedores', ''))
    productos = leer_csv(config.get('URLProductos', ''))
    tipos_negocio = leer_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQl81yJ7lo37cETniOOSzLkqwwTB6jeViKi9ebN9GweztKSL8QQ7l05pqm8LwMGMOMR0m5QCCZtOrQL/pub?gid=765886573&single=true&output=csv')
    categorias = leer_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQl81yJ7lo37cETniOOSzLkqwwTB6jeViKi9ebN9GweztKSL8QQ7l05pqm8LwMGMOMR0m5QCCZtOrQL/pub?gid=586148907&single=true&output=csv')
    unidades = leer_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQl81yJ7lo37cETniOOSzLkqwwTB6jeViKi9ebN9GweztKSL8QQ7l05pqm8LwMGMOMR0m5QCCZtOrQL/pub?gid=1563047567&single=true&output=csv')

    return jsonify({
        'proveedores': proveedores,
        'productos': productos,
        'tipos_negocio': [fila['Tipo'] for fila in tipos_negocio],
        'categorias': [fila['Categoría'] for fila in categorias],
        'unidades': [fila['Unidad'] for fila in unidades],
    })

# Ruta para nuevo proveedor
@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    config = cargar_configuracion()
    url_script = config.get("URLScriptProveedores", "")
    datos = {
        'nombre': request.form['nombre'],
        'telefono': request.form['telefono'],
        'email': request.form['email'],
        'contacto': request.form['contacto'],
        'celular': request.form['celular'],
        'tipo_negocio': request.form['tipo_negocio'],
        'observaciones': request.form['observaciones']
    }
    try:
        response = requests.post(url_script, data=datos)
        if response.status_code == 200:
            return jsonify({'mensaje': 'Proveedor guardado'})
        else:
            return jsonify({'error': 'Error al guardar proveedor'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para nuevo producto
@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    config = cargar_configuracion()
    url_script = config.get("URLScriptProductos", "")
    datos = {
        'nombre': request.form['nombre'],
        'proveedor': request.form['proveedor'],
        'categoria': request.form['categoria'],
        'unidad': request.form['unidad'],
        'observaciones': request.form['observaciones']
    }
    try:
        response = requests.post(url_script, data=datos)
        if response.status_code == 200:
            return jsonify({'mensaje': 'Producto guardado'})
        else:
            return jsonify({'error': 'Error al guardar producto'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
