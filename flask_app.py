from flask import Flask, render_template, request, redirect
from config_loader import cargar_configuracion
import pandas as pd
import requests
import os
import csv

app = Flask(__name__)

# === Configuración de rutas y archivos ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

ARCHIVO_PROVEEDORES = os.path.join(DATA_DIR, 'proveedores.csv')
ARCHIVO_PRODUCTOS = os.path.join(DATA_DIR, 'productos.csv')

# === RUTA: Página de inicio ===
@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

# === RUTA: Configuración ===
@app.route('/configuracion')
def configuracion():
    config = cargar_configuracion()
    return render_template('configuracion.html', config=config)

# === RUTA: Compras ===
@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()
    url_script = 'https://script.google.com/macros/s/AKfycbzTTyQcKoFtPyqniEfbtUXbi9XQgzHjl_fl4mJvGT4Wq2_93s3hlZPlQ9U5efruNhRr/exec'

    if request.method == 'POST':
        datos = {
            'Fecha': request.form['Fecha'],
            'N_Documento': request.form['N_Documento'],
            'Proveedor': request.form['Proveedor'],
            'Producto': request.form['Producto'],
            'Cantidad': request.form['Cantidad'],
            'PrecioUnitario': request.form['PrecioUnitario'],
            'Moneda': request.form['Moneda'],
            'Total': float(request.form['Cantidad']) * float(request.form['PrecioUnitario']),
            'Forma_Pago': request.form['Forma_Pago'],
            'Observaciones': request.form['Observaciones']
        }

        try:
            respuesta = requests.post(url_script, json=datos)
            print("📥 Respuesta del script:", respuesta.text)
        except Exception as e:
            print("❌ Error al enviar datos:", e)

        return redirect('/compras')

    # Cargar proveedores desde CSV
    proveedores = []
    if os.path.isfile(ARCHIVO_PROVEEDORES):
        try:
            with open(ARCHIVO_PROVEEDORES, newline='', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                proveedores = [fila['Nombre'] for fila in reader if fila['Nombre']]
        except Exception as e:
            print("⚠️ Error leyendo proveedores:", e)

    # Cargar productos desde CSV
    productos = []
    if os.path.isfile(ARCHIVO_PRODUCTOS):
        try:
            with open(ARCHIVO_PRODUCTOS, newline='', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                productos = [fila['Nombre'] for fila in reader if fila['Nombre']]
        except Exception as e:
            print("⚠️ Error leyendo productos:", e)

    return render_template('compras.html',
                           config=config,
                           proveedores=proveedores,
                           productos=productos)

# === RUTA: Registro de Proveedores ===
@app.route('/proveedores', methods=['GET', 'POST'])
def registrar_proveedor():
    tipos = ['Librería', 'Suministros', 'Servicios', 'Otros']

    if request.method == 'POST':
        datos = {
            'Nombre': request.form['Nombre'],
            'Teléfono': request.form['Teléfono'],
            'Email': request.form['Email'],
            'Contacto': request.form['Contacto'],
            'Celular': request.form['Celular'],
            'Tipo': request.form['Tipo'],
            'Observaciones': request.form['Observaciones']
        }

        archivo_existe = os.path.isfile(ARCHIVO_PROVEEDORES)
        with open(ARCHIVO_PROVEEDORES, 'a', newline='', encoding='utf-8') as archivo:
            writer = csv.DictWriter(archivo, fieldnames=datos.keys())
            if not archivo_existe:
                writer.writeheader()
            writer.writerow(datos)

        return redirect('/proveedores')

    return render_template('proveedores.html', tipos=tipos)

# === RUTA: Registro de Productos ===
@app.route('/productos', methods=['GET', 'POST'])
def registrar_producto():
    # Cargar proveedores para la lista desplegable
    lista_proveedores = []
    if os.path.isfile(ARCHIVO_PROVEEDORES):
        try:
            with open(ARCHIVO_PROVEEDORES, newline='', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                lista_proveedores = [fila['Nombre'] for fila in reader if fila['Nombre']]
        except Exception as e:
            print("⚠️ Error leyendo proveedores:", e)

    categorias = ['Bebidas', 'Alimentos', 'Limpieza', 'Tecnología', 'Otros']
    unidades = ['Unidad', 'Litro', 'Metro', 'Caja', 'Bolsa']

    if request.method == 'POST':
        datos = {
            'Nombre': request.form['Nombre'],
            'Categoría': request.form['Categoría'],
            'Unidad': request.form['Unidad'],
            'Proveedor': request.form['Proveedor'],
            'Observaciones': request.form['Observaciones']
        }

        archivo_existe = os.path.isfile(ARCHIVO_PRODUCTOS)
        with open(ARCHIVO_PRODUCTOS, 'a', newline='', encoding='utf-8') as archivo:
            writer = csv.DictWriter(archivo, fieldnames=datos.keys())
            if not archivo_existe:
                writer.writeheader()
            writer.writerow(datos)

        return redirect('/productos')

    return render_template('productos.html',
                           categorias=categorias,
                           unidades=unidades,
                           proveedores=lista_proveedores)

# === Ejecutar App ===
if __name__ == '__main__':
    app.run(debug=True)




