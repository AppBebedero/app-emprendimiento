from flask import Flask, render_template, request, redirect, flash
from config_loader import cargar_configuracion
import pandas as pd
import requests
import os
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'

os.makedirs("data", exist_ok=True)

def leer_csv(ruta):
    try:
        return pd.read_csv(ruta)
    except:
        return pd.DataFrame()

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

    # Precarga rápida
    proveedores = leer_csv('data/proveedores.csv')['Nombre'].dropna().tolist()
    productos = leer_csv('data/productos.csv')['Nombre'].dropna().tolist()
    categorias = leer_csv('data/categorias.csv')['Categoría'].dropna().tolist()
    unidades = leer_csv('data/unidades.csv')['Unidad'].dropna().tolist()

    seleccionado_proveedor = request.args.get("seleccionado", "")
    producto_seleccionado = request.args.get("producto", "")

    return render_template('compras.html',
                           proveedores=proveedores,
                           productos=productos,
                           categorias=categorias,
                           unidades=unidades,
                           seleccionado=seleccionado_proveedor,
                           producto_seleccionado=producto_seleccionado)

@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    config = cargar_configuracion()
    url_script = config.get('URLScriptProveedores', '')

    nombre = request.form['NombreProveedor'].strip()
    contacto = request.form['ContactoProveedor'].strip()
    telefono = request.form['TelefonoProveedor'].strip()
    tipo = request.form['TipoProveedor'].strip()

    existentes = leer_csv('data/proveedores.csv')['Nombre'].str.lower().dropna().tolist()

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

    existentes = leer_csv('data/productos.csv')['Nombre'].str.lower().dropna().tolist()

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
        except Exception as e:
            flash("❌ Error al guardar el producto.")
            print("Error en nuevo_producto:", e)

    return redirect(f"/compras?producto={nombre}")

if __name__ == '__main__':
    app.run(debug=True)

