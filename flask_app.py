from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import csv
import json
from werkzeug.utils import secure_filename
from config_loader import cargar_configuracion

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'

# ————— Rutas de disco —————
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_IMG_DIR = os.path.join(BASE_DIR, 'static', 'img')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_IMG_DIR, exist_ok=True)

# ————— Carga de configuración inicial —————
config = cargar_configuracion()

# ————— Extensiones permitidas para logo —————
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ————— Variables globales para las plantillas —————
@app.context_processor
def inject_globals():
    # Logo: preferimos la URL guardada en la hoja, si existe; si no, usamos el estático
    logo_url = config.get('LogoURL')
    if not logo_url:
        logo_url = url_for('static', filename='img/logo.png')
    return {
        'logo_exists': bool(logo_url),
        'logo_url': logo_url,
        'color_principal': config.get('ColorPrincipal', '#0d6efd'),
        'color_fondo': config.get('ColorFondo', '#ffffff'),
    }

# ————— Helpers para leer CSV —————
def leer_csv_como_diccionario(ruta_csv):
    try:
        with open(ruta_csv, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except:
        return []

def leer_lista_simple(ruta_csv):
    try:
        with open(ruta_csv, newline='', encoding='utf-8') as f:
            return [
                fila[0] for fila in csv.reader(f)
                if fila and fila[0].strip() and fila[0] != 'Seleccione uno'
            ]
    except:
        return []

# ————— Ruta de inicio —————
@app.route('/')
def inicio():
    return render_template('inicio.html')

# ————— Configuración (logo + colores) —————
@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    if request.method == 'POST':
        # 1) Procesar subida de logo
        file = request.files.get('logo')
        if file and allowed_file(file.filename):
            ext = os.path.splitext(file.filename)[1]
            tmp_name = secure_filename('logo' + ext)
            tmp_path = os.path.join(STATIC_IMG_DIR, tmp_name)
            file.save(tmp_path)
            # Asegurarnos de que siempre tengamos logo.png
            final_logo = os.path.join(STATIC_IMG_DIR, 'logo.png')
            if ext.lower() != '.png':
                os.replace(tmp_path, final_logo)
            logo_url = url_for('static', filename='img/logo.png', _external=True)
        else:
            logo_url = config.get('LogoURL', '')

        # 2) Leer colores del formulario
        cp = request.form.get('ColorPrincipal')
        cf = request.form.get('ColorFondo')

        # 3) Enviar cada cambio al Apps Script para que grabe en la hoja
        script_url = config.get('URLScriptConfig')
        if script_url:
            for clave, valor in [
                ('LogoURL', logo_url),
                ('ColorPrincipal', cp),
                ('ColorFondo', cf)
            ]:
                try:
                    requests.post(script_url, json={'Clave': clave, 'Valor': valor})
                except Exception as e:
                    print(f"❌ Error al actualizar {clave}:", e)

        return redirect(url_for('configuracion'))

    return render_template('configuracion.html', config=config)

# ————— Compras —————
@app.route('/compras', methods=['GET', 'POST'])
def compras():
    if request.method == 'POST':
        try:
            d = request.form
            datos = {
                'Fecha': d['Fecha'],
                'N_Documento': d['N_Documento'],
                'Proveedor': d['Proveedor'],
                'Producto': d['Producto'],
                'Cantidad': d['Cantidad'],
                'PrecioUnitario': d['PrecioUnitario'],
                'Moneda': config.get('Moneda', ''),
                'Total': str(float(d['Cantidad']) * float(d['PrecioUnitario'])),
                'Forma_Pago': d['Forma_Pago'],
                'Observaciones': d['Observaciones'],
                'tipo': 'compras'
            }
            # Guardar en CSV local
            path = os.path.join(DATA_DIR, 'compras.csv')
            nuevo = not os.path.exists(path)
            with open(path, 'a', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=datos.keys())
                if nuevo: w.writeheader()
                w.writerow(datos)
            # Enviar a Google Sheets
            url = config.get('URLScript')
            if url: requests.post(url, json=datos)
            return jsonify({'mensaje': 'Guardado correctamente'}), 200
        except Exception as e:
            print("❌ Error en /compras:", e)
            return jsonify({'error': 'Error interno'}), 500

    formas = ["Efectivo", "SINPE", "Tarjeta Cr."]
    return render_template('compras.html',
                           formas_pago=formas,
                           moneda=config.get('Moneda', ''))

# ————— Datos para formularios —————
@app.route('/datos_formulario')
def datos_formulario():
    return jsonify({
        'proveedores': leer_csv_como_diccionario(os.path.join(DATA_DIR, 'proveedores.csv')),
        'productos': leer_csv_como_diccionario(os.path.join(DATA_DIR, 'productos.csv')),
        'tipos_negocio': leer_lista_simple(os.path.join(DATA_DIR, 'tipos_negocio.csv')),
        'categorias': leer_lista_simple(os.path.join(DATA_DIR, 'categorias.csv')),
        'unidades': leer_lista_simple(os.path.join(DATA_DIR, 'unidades.csv'))
    })

# ————— Nuevo proveedor —————
@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    try:
        d = request.form
        nombre = d.get('nombre', '').strip()
        tipo = d.get('tipo_negocio', '').strip()
        if not nombre or not tipo:
            return jsonify({'error': 'Nombre y tipo de negocio son obligatorios'}), 400

        path = os.path.join(DATA_DIR, 'proveedores.csv')
        existentes = leer_csv_como_diccionario(path)
        if any(p['Nombre'].strip().lower() == nombre.lower() for p in existentes):
            return jsonify({'error': 'Ya existe un proveedor con ese nombre'}), 400

        nuevo = {
            'Nombre': nombre,
            'Teléfono': d.get('telefono', ''),
            'Email': d.get('email', ''),
            'Contacto': d.get('contacto', ''),
            'Celular': d.get('celular', ''),
            'Tipo_de_Negocio': tipo,
            'Observaciones': d.get('observaciones', ''),
            'tipo': 'proveedor'
        }
        with open(path, 'a', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=nuevo.keys())
            if not existentes: w.writeheader()
            w.writerow(nuevo)

        url = config.get('URLScriptProveedores')
        if url: requests.post(url, json=nuevo)
        return jsonify({'mensaje': 'Proveedor guardado'}), 200
    except Exception as e:
        print("❌ Error en nuevo_proveedor:", e)
        return jsonify({'error': 'Error interno'}), 500

# ————— Nuevo producto —————
@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    try:
        d = request.form
        nombre = d.get('nombre', '').strip()
        if not nombre:
            return jsonify({'error': 'Nombre es obligatorio'}), 400

        path = os.path.join(DATA_DIR, 'productos.csv')
        existentes = leer_csv_como_diccionario(path)
        if any(p['Nombre'].strip().lower() == nombre.lower() for p in existentes):
            return jsonify({'error': 'Ya existe un producto con ese nombre'}), 400

        nuevo = {
            'Nombre': nombre,
            'Proveedor': d.get('proveedor', ''),
            'Categoría': d.get('categoria', ''),
            'Unidad': d.get('unidad', ''),
            'Observaciones': d.get('observaciones', ''),
            'tipo': 'producto'
        }
        with open(path, 'a', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=nuevo.keys())
            if not existentes: w.writeheader()
            w.writerow(nuevo)

        url = config.get('URLScriptProductos')
        if url: requests.post(url, json=nuevo)
        return jsonify({'mensaje': 'Producto guardado'}), 200
    except Exception as e:
        print("❌ Error en nuevo_producto:", e)
        return jsonify({'error': 'Error interno'}), 500

# ————— Vistas de mantenimiento independientes —————
@app.route('/proveedores')
def proveedores():
    datos = leer_csv_como_diccionario(os.path.join(DATA_DIR, 'proveedores.csv'))
    return render_template('proveedores.html', proveedores=datos)

@app.route('/productos')
def productos():
    datos = leer_csv_como_diccionario(os.path.join(DATA_DIR, 'productos.csv'))
    return render_template('productos.html', productos=datos)

# ————— Rutas para el resto del menú —————
@app.route('/ventas/facturacion')
def facturacion():
    return render_template('facturacion.html')

@app.route('/clientes')
def clientes():
    return render_template('clientes.html')

@app.route('/costos')
def costos():
    return render_template('costos.html')

@app.route('/finanzas')
def finanzas():
    return render_template('finanzas.html')

@app.route('/reportes')
def reportes():
    return render_template('reportes.html')

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

if __name__ == '__main__':
    app.run(debug=True)
