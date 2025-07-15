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

def leer_csv_simple(ruta):
    try:
        df = pd.read_csv(ruta)
        return df['Opción'].dropna().tolist()
    except:
        return []

@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    config = cargar_configuracion()
    return render_template('configuracion.html', config=config)

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()
    url_script = config.get('URLScript', '')

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
            flash("✅ Compra guardada correctamente.")
        except Exception as e:
            flash("❌ Error al guardar la compra.")
            print("Error compras:", e)
        return redirect('/compras')

    proveedores = leer_csv_simple('data/proveedores.csv')
    productos = leer_csv_simple('data/productos.csv')

    seleccionado_proveedor = request.args.get("seleccionado", "")
    seleccionado_producto = request.args.get("producto", "")

    return render_template('compras.html',
                           config=config,
                           proveedores=proveedores,
                           productos=productos,
                           seleccionado=seleccionado_proveedor,
                           producto_seleccionado=seleccionado_producto)

@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    config = cargar_configuracion()
    url_script = config.get('URLScriptProveedores', '')

    nombre = request.form['NombreProveedor'].strip()
    contacto = request.form['ContactoProveedor'].strip()
    telefono = request.form['TelefonoProveedor'].strip()
    tipo = request.form['TipoNegocioProveedor'].strip()

    archivo_local = 'data/proveedores.csv'
    existentes = []
    if os.path.exists(archivo_local):
        try:
            df = pd.read_csv(archivo_local)
            existentes = [p.strip().lower() for p in df['Opción'].dropna().tolist()]
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
            'Tipo': tipo,
            'Observaciones': ''
        }
        try:
            requests.post(url_script, json=datos)
            flash("✅ Proveedor agregado correctamente.")
            with open(archivo_local, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([nombre])
        except Exception as e:
            flash("❌ Error al guardar el proveedor.")
            print("Error en nuevo_proveedor:", e)

    return redirect(f"/compras?seleccionado={nombre}")

@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    config = cargar_configuracion()
    url_script = config.get('URLScriptProductos', '')

    nombre = request.form['NombreProducto'].strip()
    categoria = request.form['CategoriaProducto'].strip()
    unidad = request.form['UnidadProducto'].strip()

    archivo_local = 'data/productos.csv'
    existentes = []
    if os.path.exists(archivo_local):
        try:
            df = pd.read_csv(archivo_local)
            existentes = [p.strip().lower() for p in df['Opción'].dropna().tolist()]
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
        try:
            requests.post(url_script, json=datos)
            flash("✅ Producto agregado correctamente.")
            with open(archivo_local, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([nombre])
        except Exception as e:
            flash("❌ Error al guardar el producto.")
            print("Error en nuevo_producto:", e)

    return redirect(f"/compras?producto={nombre}")

if __name__ == '__main__':
    app.run(debug=True)
