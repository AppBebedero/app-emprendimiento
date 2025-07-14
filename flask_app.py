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

# Función para descargar CSV desde Google Sheets
def descargar_csv(desde_url, hacia_archivo):
    try:
        respuesta = requests.get(desde_url)
        if respuesta.status_code == 200:
            with open(hacia_archivo, 'w', encoding='utf-8') as f:
                f.write(respuesta.text)
            print(f"✅ CSV actualizado: {hacia_archivo}")
        else:
            print(f"❌ Error al descargar CSV: {respuesta.status_code}")
    except Exception as e:
        print("❌ Error al descargar CSV:", e)

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

    # Precarga desde CSV
    proveedores, productos = [], []
    try:
        df_prov = pd.read_csv('data/proveedores.csv')
        proveedores = df_prov['Nombre'].dropna().tolist()
    except: pass
    try:
        df_prod = pd.read_csv('data/productos.csv')
        productos = df_prod['Nombre'].dropna().tolist()
    except: pass

    seleccionado = request.args.get("seleccionado", "")

    return render_template('compras.html', config=config,
                           proveedores=proveedores,
                           productos=productos,
                           seleccionado=seleccionado)

@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    config = cargar_configuracion()
    url_script = config.get('URLScriptProveedores', '')
    hoja_id = '1AGm3J7Jv5zxbKpQ-M8fveoV2-41xdb2OSYSkyKRyhlg'
    gid = '129758967'
    url_csv = f'https://docs.google.com/spreadsheets/d/{hoja_id}/export?format=csv&gid={gid}'
    archivo_local = 'data/proveedores.csv'

    nombre = request.form['NombreProveedor'].strip()
    contacto = request.form['ContactoProveedor'].strip()
    telefono = request.form['TelefonoProveedor'].strip()

    existentes = []
    if os.path.exists(archivo_local):
        try:
            df = pd.read_csv(archivo_local)
            existentes = [p.strip().lower() for p in df['Nombre'].dropna().tolist()]
        except: pass

    if nombre.lower() in existentes:
        flash("⚠️ Ya existe un proveedor con ese nombre.")
        return redirect('/compras')

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

    try:
        requests.post(url_script, json=datos)
        flash("✅ Proveedor agregado correctamente.")
        descargar_csv(url_csv, archivo_local)
        print("📝 Proveedores actuales:", pd.read_csv(archivo_local)['Nombre'].tolist())
    except Exception as e:
        flash("❌ Error al guardar el proveedor.")
        print("Error en nuevo_proveedor:", e)

    return redirect(f"/compras?seleccionado={nombre}")

@app.route('/proveedores', methods=['GET', 'POST'])
def proveedores():
    config = cargar_configuracion()
    url_script = config.get('URLScriptProveedores', '')
    hoja_id = '1AGm3J7Jv5zxbKpQ-M8fveoV2-41xdb2OSYSkyKRyhlg'
    gid = '129758967'
    url_csv = f'https://docs.google.com/spreadsheets/d/{hoja_id}/export?format=csv&gid={gid}'
    archivo_local = 'data/proveedores.csv'

    descargar_csv(url_csv, archivo_local)

    existentes = []
    if os.path.exists(archivo_local):
        try:
            df = pd.read_csv(archivo_local)
            existentes = [p.strip().lower() for p in df['Nombre'].dropna().tolist()]
        except: pass

    if request.method == 'POST':
        nombre_nuevo = request.form['Nombre'].strip().lower()
        datos = {
            'tipo': 'proveedor',
            'Nombre': request.form['Nombre'].strip(),
            'Teléfono': request.form['Telefono'],
            'Email': request.form['Email'],
            'Contacto': request.form['Contacto'],
            'Celular': request.form['Celular'],
            'Tipo': request.form['Tipo'],
            'Observaciones': request.form['Observaciones']
        }

        duplicado = any(nombre_nuevo in p or p in nombre_nuevo for p in existentes)
        if duplicado:
            flash("⚠️ Ya existe un proveedor con nombre similar.")
        else:
            try:
                requests.post(url_script, json=datos)
                flash("✅ Proveedor registrado correctamente.")
                descargar_csv(url_csv, archivo_local)
            except Exception as e:
                flash("❌ Error al guardar el proveedor.")
                print("Error proveedores:", e)
        return redirect('/proveedores')

    return render_template('proveedores.html')

@app.route('/productos', methods=['GET', 'POST'])
def productos():
    config = cargar_configuracion()
    url_script = config.get('URLScriptProductos', '')
    hoja_id = '1AGm3J7Jv5zxbKpQ-M8fveoV2-41xdb2OSYSkyKRyhlg'
    gid = '491018015'
    url_csv = f'https://docs.google.com/spreadsheets/d/{hoja_id}/export?format=csv&gid={gid}'
    archivo_local = 'data/productos.csv'

    descargar_csv(url_csv, archivo_local)

    existentes, proveedores = [], []
    try:
        df_prov = pd.read_csv('data/proveedores.csv')
        proveedores = df_prov['Nombre'].dropna().tolist()
    except: pass
    try:
        df_prod = pd.read_csv(archivo_local)
        existentes = [p.strip().lower() for p in df_prod['Nombre'].dropna().tolist()]
    except: pass

    if request.method == 'POST':
        nombre_nuevo = request.form['Nombre'].strip().lower()
        datos = {
            'tipo': 'producto',
            'Nombre': request.form['Nombre'].strip(),
            'Categoría': request.form['Categoría'],
            'Unidad': request.form['Unidad'],
            'Proveedor': request.form['Proveedor'],
            'Observaciones': request.form['Observaciones']
        }

        duplicado = any(nombre_nuevo in p or p in nombre_nuevo for p in existentes)
        if duplicado:
            flash("⚠️ Ya existe un producto con nombre similar.")
        else:
            try:
                requests.post(url_script, json=datos)
                flash("✅ Producto registrado correctamente.")
                descargar_csv(url_csv, archivo_local)
            except Exception as e:
                flash("❌ Error al guardar el producto.")
                print("Error productos:", e)
        return redirect('/productos')

    return render_template('productos.html', proveedores=proveedores)

if __name__ == '__main__':
    app.run(debug=True)
