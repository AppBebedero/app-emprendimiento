from flask import Flask, render_template, request, redirect, jsonify
from config_loader import cargar_configuracion
import requests
import csv
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Leer archivo CSV simple
def leer_lista_csv(nombre_archivo):
    ruta = os.path.join("data", nombre_archivo)
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            return [linea.strip() for linea in f if linea.strip()]
    return []

# --- Rutas generales ---

@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()
    if request.method == 'POST':
        datos = {
            'Fecha': request.form.get('Fecha'),
            'N_Documento': request.form.get('N_Documento'),
            'Proveedor': request.form.get('Proveedor'),
            'Producto': request.form.get('Producto'),
            'Cantidad': request.form.get('Cantidad'),
            'PrecioUnitario': request.form.get('PrecioUnitario'),
            'Moneda': request.form.get('Moneda'),
            'Forma_Pago': request.form.get('Forma_Pago'),
            'Observaciones': request.form.get('Observaciones', '')
        }
        try:
            respuesta = requests.post(config['URLScript'], data=datos)
            if respuesta.status_code == 200:
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "error": "Error al guardar en Google Sheets"}), 500
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    formas_pago = ['Efectivo', 'SINPE', 'Tarjeta Cr.']
    return render_template('compras.html', formas_pago=formas_pago)

@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    config = cargar_configuracion()
    nombre = request.form.get('nombre')
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400

    datos = {
        'nombre': nombre,
        'telefono': request.form.get('telefono'),
        'email': request.form.get('email'),
        'contacto': request.form.get('contacto'),
        'celular': request.form.get('celular'),
        'tipo_negocio': request.form.get('tipo_negocio'),
        'observaciones': request.form.get('observaciones', '')
    }

    try:
        respuesta = requests.post(config['URLScriptProveedores'], data=datos)
        if respuesta.status_code == 200:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Error al guardar en Google Sheets"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    config = cargar_configuracion()
    nombre = request.form.get('nombre')
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400

    datos = {
        'nombre': nombre,
        'proveedor': request.form.get('proveedor'),
        'categoria': request.form.get('categoria'),
        'unidad': request.form.get('unidad'),
        'observaciones': request.form.get('observaciones', '')
    }

    try:
        respuesta = requests.post(config['URLScriptProductos'], data=datos)
        if respuesta.status_code == 200:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Error al guardar en Google Sheets"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/datos_formulario')
def datos_formulario():
    config = cargar_configuracion()
    proveedores = []
    productos = []

    try:
        resp_p = requests.get(config['URLProveedores'])
        if resp_p.ok:
            reader = csv.DictReader(resp_p.text.splitlines())
            proveedores = [row for row in reader if row.get('Nombre')]

        resp_prod = requests.get(config['URLProductos'])
        if resp_prod.ok:
            reader = csv.DictReader(resp_prod.text.splitlines())
            productos = [row for row in reader if row.get('Nombre')]

    except Exception as e:
        print("⚠️ Error cargando proveedores/productos:", e)

    tipos_negocio = leer_lista_csv("tipos_negocio.csv")
    categorias = leer_lista_csv("categorias.csv")
    unidades = leer_lista_csv("unidades.csv")

    return jsonify({
        "proveedores": proveedores,
        "productos": productos,
        "tipos_negocio": tipos_negocio,
        "categorias": categorias,
        "unidades": unidades
    })

# Ruta para configuración futura
@app.route('/configuracion')
def configuracion():
    config = cargar_configuracion()
    return render_template('configuracion.html', config=config)

# --- Ejecutar ---
if __name__ == '__main__':
    app.run(debug=True)
