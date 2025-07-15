from flask import Flask, render_template, request, redirect, flash
from config_loader import cargar_configuracion
import pandas as pd
import requests
import os
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'

# Crear carpeta /data si no existe
os.makedirs("data", exist_ok=True)

# --- Utilidad para cargar listas desde CSV ---
def cargar_lista_desde_csv(ruta):
    try:
        df = pd.read_csv(ruta)
        return df.iloc[:, 0].dropna().tolist()
    except:
        return []

# --- Utilidad para guardar datos nuevos en CSV ---
def guardar_en_csv(nombre_archivo, encabezados, datos):
    existe = os.path.exists(nombre_archivo)
    with open(nombre_archivo, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=encabezados)
        if not existe:
            writer.writeheader()
        writer.writerow(datos)

@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()
    url_script = config.get('URLScript', '')

    # Precarga desde CSV local
    proveedores = cargar_lista_desde_csv('data/proveedores.csv')
    productos = cargar_lista_desde_csv('data/productos.csv')
    formas_pago = ['Efectivo', 'SINPE', 'Tarjeta Cr.']
    monedas = ['CRC', 'USD']

    # Parámetros seleccionados si vienen de los formularios modales
    seleccionado = request.args.get('seleccionado', '')
    producto_seleccionado = request.args.get('producto', '')

    if request.method == 'POST':
        datos = {
            'tipo': 'compras',
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
            requests.post(url_script, json=datos)
            flash("✅ Compra registrada correctamente.")
        except Exception as e:
            flash("❌ Error al guardar la compra.")
            print("Error compras:", e)
        return redirect('/compras')

    return render_template('compras.html',
                           proveedores=proveedores,
                           productos=productos,
                           formas_pago=formas_pago,
                           monedas=monedas,
                           seleccionado=seleccionado,
                           producto_seleccionado=producto_seleccionado)

@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    nombre = request.form['NombreProveedor'].strip()
    telefono = request.form['TelefonoProveedor'].strip()
    contacto = request.form['ContactoProveedor'].strip()
    tipo = request.form['TipoProveedor'].strip()

    existentes = cargar_lista_desde_csv('data/proveedores.csv')
    if nombre.lower() in [p.lower() for p in existentes]:
        flash("⚠️ Ya existe un proveedor con ese nombre.")
    else:
        datos = {
            'Nombre': nombre,
            'Teléfono': telefono,
            'Email': '',
            'Contacto': contacto,
            'Celular': '',
            'Tipo de Negocio': tipo,
            'Observaciones': ''
        }
        guardar_en_csv('data/proveedores.csv',
                       ['Nombre', 'Teléfono', 'Email', 'Contacto', 'Celular', 'Tipo de Negocio', 'Observaciones'],
                       datos)
        flash("✅ Proveedor agregado correctamente.")
    return redirect(f'/compras?seleccionado={nombre}')

@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    nombre = request.form['NombreProducto'].strip()
    categoria = request.form['CategoriaProducto'].strip()
    unidad = request.form['UnidadProducto'].strip()

    existentes = cargar_lista_desde_csv('data/productos.csv')
    if nombre.lower() in [p.lower() for p in existentes]:
        flash("⚠️ Ya existe un producto con ese nombre.")
    else:
        datos = {
            'Nombre': nombre,
            'Categoría': categoria,
            'Unidad': unidad,
            'Proveedor': '',
            'Observaciones': ''
        }
        guardar_en_csv('data/productos.csv',
                       ['Nombre', 'Categoría', 'Unidad', 'Proveedor', 'Observaciones'],
                       datos)
        flash("✅ Producto agregado correctamente.")
    return redirect(f'/compras?producto={nombre}')

if __name__ == '__main__':
    app.run(debug=True)
