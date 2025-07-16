from flask import Flask, render_template, request, redirect, jsonify
from config_loader import cargar_configuracion
import pandas as pd
import requests
import os
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'

# Carpeta para archivos locales CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Leer archivo CSV como lista de diccionarios
def leer_csv_como_diccionario(ruta_csv):
    try:
        with open(ruta_csv, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except:
        return []

# Leer archivo CSV como lista simple (una columna)
def leer_lista_simple(ruta_csv):
    try:
        with open(ruta_csv, newline='', encoding='utf-8') as f:
            return [fila[0] for fila in csv.reader(f) if fila and fila[0].strip() and fila[0] != 'Seleccione uno']
    except:
        return []

# Ruta principal
@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

# Ruta para el formulario de compras
@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()

    if request.method == 'POST':
        try:
            url_script = config.get('URLScript', '')
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
            respuesta = requests.post(url_script, data=datos)
            print("📥 Respuesta del script:", respuesta.text)
            if respuesta.ok:
                return jsonify({"mensaje": "Guardado correctamente"}), 200
            else:
                return jsonify({"error": "Error al guardar"}), 400
        except Exception as e:
            print("❌ Error:", e)
            return jsonify({"error": "Error interno"}), 500

    formas_pago = ["Efectivo", "SINPE", "Tarjeta Cr."]
    return render_template('compras.html', formas_pago=formas_pago)

# Ruta que devuelve datos para los formularios (proveedores, productos, listas)
@app.route('/datos_formulario')
def datos_formulario():
    proveedores = leer_csv_como_diccionario(os.path.join(DATA_DIR, 'proveedores.csv'))
    productos = leer_csv_como_diccionario(os.path.join(DATA_DIR, 'productos.csv'))
    tipos_negocio = leer_lista_simple(os.path.join(DATA_DIR, 'tipos_negocio.csv'))
    categorias = leer_lista_simple(os.path.join(DATA_DIR, 'categorias.csv'))
    unidades = leer_lista_simple(os.path.join(DATA_DIR, 'unidades.csv'))

    return jsonify({
        'proveedores': proveedores,
        'productos': productos,
        'tipos_negocio': tipos_negocio,
        'categorias': categorias,
        'unidades': unidades
    })

# Ruta para registrar nuevo proveedor
@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    config = cargar_configuracion()
    try:
        data = request.form
        nombre = data.get('nombre').strip()
        tipo_negocio = data.get('tipo_negocio').strip()

        if not nombre or not tipo_negocio:
            return jsonify({'error': 'Nombre y Tipo de Negocio son obligatorios'}), 400

        # Verificar duplicados
        ruta = os.path.join(DATA_DIR, 'proveedores.csv')
        existentes = leer_csv_como_diccionario(ruta)
        if any(p['Nombre'].strip().lower() == nombre.lower() for p in existentes):
            return jsonify({'error': 'Ya existe un proveedor con ese nombre'}), 400

        nuevo = {
            'Nombre': nombre,
            'Teléfono': data.get('telefono', ''),
            'Email': data.get('email', ''),
            'Contacto': data.get('contacto', ''),
            'Celular': data.get('celular', ''),
            'Tipo de Negocio': tipo_negocio,
            'Observaciones': data.get('observaciones', '')
        }

        # Guardar localmente
        archivo_nuevo = not os.path.exists(ruta)
        with open(ruta, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=nuevo.keys())
            if archivo_nuevo:
                writer.writeheader()
            writer.writerow(nuevo)

        # Enviar a Google
        url_script = config.get('URLScriptProveedores', '')
        requests.post(url_script, data=nuevo)

        return jsonify({'mensaje': 'Proveedor guardado'}), 200
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({'error': 'Error interno'}), 500

# Ruta para registrar nuevo producto
@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    config = cargar_configuracion()
    try:
        data = request.form
        nombre = data.get('nombre').strip()
        proveedor = data.get('proveedor').strip()
        categoria = data.get('categoria').strip()
        unidad = data.get('unidad').strip()

        if not nombre or not proveedor or not categoria or not unidad:
            return jsonify({'error': 'Todos los campos son obligatorios, excepto observaciones'}), 400

        # Verificar duplicados
        ruta = os.path.join(DATA_DIR, 'productos.csv')
        existentes = leer_csv_como_diccionario(ruta)
        if any(p['Nombre'].strip().lower() == nombre.lower() for p in existentes):
            return jsonify({'error': 'Ya existe un producto con ese nombre'}), 400

        nuevo = {
            'Nombre': nombre,
            'Proveedor': proveedor,
            'Categoría': categoria,
            'Unidad': unidad,
            'Observaciones': data.get('observaciones', '')
        }

        # Guardar localmente
        archivo_nuevo = not os.path.exists(ruta)
        with open(ruta, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=nuevo.keys())
            if archivo_nuevo:
                writer.writeheader()
            writer.writerow(nuevo)

        # Enviar a Google
        url_script = config.get('URLScriptProductos', '')
        requests.post(url_script, data=nuevo)

        return jsonify({'mensaje': 'Producto guardado'}), 200
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({'error': 'Error interno'}), 500

# Iniciar servidor
if __name__ == '__main__':
    app.run(debug=True)
