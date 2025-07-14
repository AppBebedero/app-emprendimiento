from flask import Flask, render_template, request, redirect, flash
from config_loader import cargar_configuracion
import pandas as pd
import requests
import os
import csv
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'

# Crear carpeta local para archivos
os.makedirs("data", exist_ok=True)

# Utilidad para guardar en CSV local
def guardar_en_csv(ruta, encabezados, fila):
    existe = os.path.exists(ruta)
    with open(ruta, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=encabezados)
        if not existe:
            writer.writeheader()
        writer.writerow(fila)

# Utilidad para sincronizar con Google Sheets
def sincronizar_con_google(url_script, datos):
    try:
        requests.post(url_script, json=datos)
        print("✅ Sincronizado con Google Sheets")
    except Exception as e:
        print("❌ Error al sincronizar:", e)

@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()
    url_script = config.get('URLScript', '')
    ruta_csv = 'data/compras.csv'

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
        guardar_en_csv(ruta_csv, list(datos.keys()), datos)
        threading.Thread(target=sincronizar_con_google, args=(url_script, datos)).start()
        flash("✅ Compra registrada localmente. Se sincronizará pronto.")
        return redirect('/compras')

    # Cargar proveedores y productos desde CSV local
    proveedores, productos = [], []
    try:
        df_prov = pd.read_csv('data/proveedores.csv')
        proveedores = df_prov['Nombre'].dropna().tolist()
    except: pass
    try:
        df_prod = pd.read_csv('data/productos.csv')
        productos = df_prod['Nombre'].dropna().tolist()
    except: pass

    return render_template('compras.html',
                           config=config,
                           proveedores=proveedores,
                           productos=productos,
                           seleccionado=request.args.get("seleccionado", ""),
                           producto_seleccionado=request.args.get("producto", ""))

@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    config = cargar_configuracion()
    url_script = config.get('URLScriptProveedores', '')
    ruta_csv = 'data/proveedores.csv'

    nombre = request.form['NombreProveedor'].strip()
    contacto = request.form['ContactoProveedor'].strip()
    telefono = request.form['TelefonoProveedor'].strip()

    existentes = []
    if os.path.exists(ruta_csv):
        try:
            df = pd.read_csv(ruta_csv)
            existentes = [p.strip().lower() for p in df['Nombre'].dropna().tolist()]
        except: pass

    if nombre.lower() in existentes:
        flash("⚠️ Ya existe un proveedor con ese nombre.")
    else:
        datos = {
            'tipo': 'proveedor',
            'Nombre': nombre,
            'Teléfono': telefono,
            'Email': '',
            'Contacto': contacto,
            'Celular': '',
            'Tipo': '',
            'Observaciones': ''
        }
        guardar_en_csv(ruta_csv, list(datos.keys()), datos)
        threading.Thread(target=sincronizar_con_google, args=(url_script, datos)).start()
        flash("✅ Proveedor agregado.")
    return redirect(f"/compras?seleccionado={nombre}")

@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    config = cargar_configuracion()
    url_script = config.get('URLScriptProductos', '')
    ruta_csv = 'data/productos.csv'

    nombre = request.form['NombreProducto'].strip()
    categoria = request.form['CategoriaProducto'].strip()
    unidad = request.form['UnidadProducto'].strip()

    existentes = []
    if os.path.exists(ruta_csv):
        try:
            df = pd.read_csv(ruta_csv)
            existentes = [p.strip().lower() for p in df['Nombre'].dropna().tolist()]
        except: pass

    if nombre.lower() in existentes:
        flash("⚠️ Ya existe un producto con ese nombre.")
    else:
        datos = {
            'tipo': 'producto',
            'Nombre': nombre,
            'Categoría': categoria,
            'Unidad': unidad,
            'Proveedor': '',
            'Observaciones': ''
        }
        guardar_en_csv(ruta_csv, list(datos.keys()), datos)
        threading.Thread(target=sincronizar_con_google, args=(url_script, datos)).start()
        flash("✅ Producto agregado.")
    return redirect(f"/compras?producto={nombre}")

@app.route('/configuracion')
def configuracion():
    config = cargar_configuracion()
    return render_template('configuracion.html', config=config)

if __name__ == '__main__':
    app.run(debug=True)
