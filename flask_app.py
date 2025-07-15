from flask import Flask, render_template, request, redirect, url_for, jsonify
import csv
import os
import requests
from config_loader import cargar_configuracion

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Utilidades CSV
def leer_csv(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def escribir_csv(ruta, datos, encabezados):
    archivo_existe = os.path.exists(ruta)
    with open(ruta, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=encabezados)
        if not archivo_existe:
            writer.writeheader()
        writer.writerow(datos)

def guardar_en_google(url_script, datos):
    try:
        requests.post(url_script, data=datos)
    except Exception as e:
        print("Error al enviar a Google Sheets:", e)

# --- Rutas ---
@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()
    proveedores = leer_csv('data/proveedores.csv')
    productos = leer_csv('data/productos.csv')
    formas_pago = ['Efectivo', 'SINPE', 'Tarjeta Cr.']
    mensaje = ''
    
    if request.method == 'POST':
        datos = {
            'Fecha': request.form['Fecha'],
            'N_Documento': request.form['N_Documento'],
            'Proveedor': request.form['Proveedor'],
            'Producto': request.form['Producto'],
            'Cantidad': request.form['Cantidad'],
            'PrecioUnitario': request.form['PrecioUnitario'],
            'Moneda': request.form['Moneda'],
            'Total': request.form['Total'],
            'Forma_Pago': request.form['Forma_Pago'],
            'Observaciones': request.form['Observaciones']
        }
        escribir_csv('data/compras.csv', datos, list(datos.keys()))
        guardar_en_google(config.get('URLScript', ''), datos)
        mensaje = '✅ Compra registrada exitosamente'

    return render_template('compras.html', proveedores=proveedores, productos=productos,
                           formas_pago=formas_pago, mensaje=mensaje)

@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    config = cargar_configuracion()
    nombre = request.form['nombre'].strip()
    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio'}), 400

    proveedores = leer_csv('data/proveedores.csv')
    if any(p['Nombre'].lower() == nombre.lower() for p in proveedores):
        return jsonify({'error': 'Ya existe un proveedor con ese nombre'}), 409

    nuevo = {
        'Nombre': nombre,
        'Teléfono': request.form.get('telefono', ''),
        'Email': request.form.get('email', ''),
        'Contacto': request.form.get('contacto', ''),
        'Celular': request.form.get('celular', ''),
        'Tipo de Negocio': request.form.get('tipo_negocio', ''),
        'Observaciones': request.form.get('observaciones', '')
    }

    escribir_csv('data/proveedores.csv', nuevo, list(nuevo.keys()))
    guardar_en_google(config.get('URLScriptProveedores', ''), nuevo)
    return jsonify({'ok': True})

@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    config = cargar_configuracion()
    nombre = request.form['nombre'].strip()
    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio'}), 400

    productos = leer_csv('data/productos.csv')
    if any(p['Nombre'].lower() == nombre.lower() for p in productos):
        return jsonify({'error': 'Ya existe un producto con ese nombre'}), 409

    nuevo = {
        'Nombre': nombre,
        'Proveedor': request.form.get('proveedor', ''),
        'Categoría': request.form.get('categoria', ''),
        'Unidad': request.form.get('unidad', ''),
        'Observaciones': request.form.get('observaciones', '')
    }

    escribir_csv('data/productos.csv', nuevo, list(nuevo.keys()))
    guardar_en_google(config.get('URLScriptProductos', ''), nuevo)
    return jsonify({'ok': True})

@app.route('/datos_formulario')
def datos_formulario():
    proveedores = leer_csv('data/proveedores.csv')
    productos = leer_csv('data/productos.csv')
    categorias = [x['Categoría'] for x in leer_csv('data/categorias.csv')]
    unidades = [x['Unidad'] for x in leer_csv('data/unidades.csv')]

    return jsonify({
        'proveedores': proveedores,
        'productos': productos,
        'categorias': categorias,
        'unidades': unidades
    })

if __name__ == '__main__':
    app.run(debug=True)
