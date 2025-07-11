from flask import Flask, render_template, request, redirect
from config_loader import cargar_configuracion
import pandas as pd
import requests
import os
import csv

app = Flask(__name__)

# Crear carpeta /data si no existe
os.makedirs("data", exist_ok=True)

# Rutas generales
@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

@app.route('/configuracion')
def configuracion():
    config = cargar_configuracion()
    return render_template('configuracion.html', config=config)

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()
    url_script = config.get('URLScript', '')

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

    # Leer listas locales
    proveedores = []
    productos = []

    try:
        df_prov = pd.read_csv('data/proveedores.csv')
        proveedores = df_prov['Nombre'].dropna().tolist()
    except Exception as e:
        print("⚠️ Error cargando proveedores:", e)

    try:
        df_prod = pd.read_csv('data/productos.csv')
        productos = df_prod['Nombre'].dropna().tolist()
    except Exception as e:
        print("⚠️ Error cargando productos:", e)

    return render_template('compras.html', config=config,
                           proveedores=proveedores,
                           productos=productos)

@app.route('/proveedores', methods=['GET', 'POST'])
def proveedores():
    if request.method == 'POST':
        datos = {
            'Nombre': request.form['Nombre'],
            'Teléfono': request.form['Telefono'],
            'Email': request.form['Email'],
            'Contacto': request.form['Contacto'],
            'Celular': request.form['Celular'],
            'Tipo': request.form['Tipo'],
            'Observaciones': request.form['Observaciones']
        }

        archivo = 'data/proveedores.csv'
        escribir_encabezado = not os.path.exists(archivo)

        with open(archivo, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=datos.keys())
            if escribir_encabezado:
                writer.writeheader()
            writer.writerow(datos)

        return redirect('/proveedores')

    return render_template('proveedores.html')

@app.route('/productos', methods=['GET', 'POST'])
def productos():
    proveedores = []
    try:
        df = pd.read_csv('data/proveedores.csv')
        proveedores = df['Nombre'].dropna().tolist()
    except:
        pass

    if request.method == 'POST':
        datos = {
            'Nombre': request.form['Nombre'],
            'Categoría': request.form['Categoría'],
            'Unidad': request.form['Unidad'],
            'Proveedor': request.form['Proveedor'],
            'Observaciones': request.form['Observaciones']
        }

        archivo = 'data/productos.csv'
        escribir_encabezado = not os.path.exists(archivo)

        with open(archivo, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=datos.keys())
            if escribir_encabezado:
                writer.writeheader()
            writer.writerow(datos)

        return redirect('/productos')

    return render_template('productos.html', proveedores=proveedores)

if __name__ == '__main__':
    app.run(debug=True)





