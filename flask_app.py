from flask import Flask, render_template, request, jsonify, redirect
import pandas as pd
import requests
import os
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def leer_csv_como_diccionario(ruta_csv):
    try:
        with open(ruta_csv, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except:
        return []

def leer_lista_simple(ruta_csv):
    try:
        with open(ruta_csv, newline='', encoding='utf-8') as f:
            return [fila[0] for fila in csv.reader(f) if fila and fila[0].strip() and fila[0] != 'Seleccione uno']
    except:
        return []

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    if request.method == 'POST':
        try:
            data = request.form
            datos = {
                'Fecha': data['Fecha'],
                'N_Documento': data['N_Documento'],
                'Proveedor': data['Proveedor'],
                'Producto': data['Producto'],
                'Cantidad': data['Cantidad'],
                'PrecioUnitario': data['PrecioUnitario'],
                'Moneda': data['Moneda'],
                'Total': str(float(data['Cantidad']) * float(data['PrecioUnitario'])),
                'Forma_Pago': data['Forma_Pago'],
                'Observaciones': data['Observaciones'],
                'tipo': 'compras'
            }

            # Guardar en CSV local
            ruta = os.path.join(DATA_DIR, 'compras.csv')
            archivo_nuevo = not os.path.exists(ruta)
            with open(ruta, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=datos.keys())
                if archivo_nuevo:
                    writer.writeheader()
                writer.writerow(datos)

            # URL fija para pruebas (sustituir la URL cargada del config)
            url_compras = 'https://script.google.com/macros/s/AKfycbzTTyQcKoFtPyqniEfbtUXbi9XQgzHjl_fl4mJvGT4Wq2_93s3hlZPlQ9U5efruNhRr/exec'
            r = requests.post(url_compras, json=datos)
            print("📥 Respuesta Google:", r.text)

            return jsonify({'mensaje': 'Guardado correctamente'}), 200
        except Exception as e:
            print("❌ Error en /compras:", e)
            return jsonify({'error': 'Error interno'}), 500

    formas_pago = ["Efectivo", "SINPE", "Tarjeta Cr."]
    return render_template('compras.html', formas_pago=formas_pago)

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

@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    try:
        data = request.form
        nombre = data.get('nombre').strip()
        tipo = data.get('tipo_negocio').strip()

        if not nombre or not tipo:
            return jsonify({'error': 'Nombre y tipo de negocio son obligatorios'}), 400

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
            'Tipo': tipo,
            'Observaciones': data.get('observaciones', ''),
            'tipo': 'proveedor'
        }

        archivo_nuevo = not os.path.exists(ruta)
        with open(ruta, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=nuevo.keys())
            if archivo_nuevo:
                writer.writeheader()
            writer.writerow(nuevo)

        url_proveedores = 'https://script.google.com/macros/s/AKfycbzTTyQcKoFtPyqniEfbtUXbi9XQgzHjl_fl4mJvGT4Wq2_93s3hlZPlQ9U5efruNhRr/exec'
        r = requests.post(url_proveedores, json=nuevo)
        print("📥 Respuesta proveedor:", r.text)

        return jsonify({'mensaje': 'Proveedor guardado'}), 200
    except Exception as e:
        print("❌ Error en nuevo_proveedor:", e)
        return jsonify({'error': 'Error interno'}), 500

@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    try:
        data = request.form
        nombre = data.get('nombre').strip()

        if not nombre:
            return jsonify({'error': 'Nombre es obligatorio'}), 400

        ruta = os.path.join(DATA_DIR, 'productos.csv')
        existentes = leer_csv_como_diccionario(ruta)
        if any(p['Nombre'].strip().lower() == nombre.lower() for p in existentes):
            return jsonify({'error': 'Ya existe un producto con ese nombre'}), 400

        nuevo = {
            'Nombre': nombre,
            'Proveedor': data.get('proveedor', ''),
            'Categoría': data.get('categoria', ''),
            'Unidad': data.get('unidad', ''),
            'Observaciones': data.get('observaciones', ''),
            'tipo': 'producto'
        }

        archivo_nuevo = not os.path.exists(ruta)
        with open(ruta, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=nuevo.keys())
            if archivo_nuevo:
                writer.writeheader()
            writer.writerow(nuevo)

        url_productos = 'https://script.google.com/macros/s/AKfycbzTTyQcKoFtPyqniEfbtUXbi9XQgzHjl_fl4mJvGT4Wq2_93s3hlZPlQ9U5efruNhRr/exec'
        r = requests.post(url_productos, json=nuevo)
        print("📥 Respuesta producto:", r.text)

        return jsonify({'mensaje': 'Producto guardado'}), 200
    except Exception as e:
        print("❌ Error en nuevo_producto:", e)
        return jsonify({'error': 'Error interno'}), 500

if __name__ == '__main__':
    app.run(debug=True)
