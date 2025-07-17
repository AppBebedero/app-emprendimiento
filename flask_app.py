from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import csv
from werkzeug.utils import secure_filename
from config_loader import cargar_configuracion

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'

# Directorios base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_IMG_DIR = os.path.join(BASE_DIR, 'static', 'img')

# Asegurar que existan
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_IMG_DIR, exist_ok=True)

# Configuración de subida de logo
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Cargar la configuración una sola vez
config = cargar_configuracion()

# Inyectar variables globales en todas las plantillas
@app.context_processor
def inject_globals():
    logo_path = os.path.join(STATIC_IMG_DIR, 'logo.png')
    return {
        'logo_exists': os.path.exists(logo_path),
        'logo_url': url_for('static', filename='img/logo.png'),
        'color_principal': config.get('ColorPrincipal', '#0d6efd')
    }

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
                fila[0]
                for fila in csv.reader(f)
                if fila and fila[0].strip() and fila[0] != 'Seleccione uno'
            ]
    except:
        return []

@app.route('/')
def inicio():
    return render_template(
        'inicio.html',
        config=config
    )

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    if request.method == 'POST':
        file = request.files.get('logo')
        if file and allowed_file(file.filename):
            ext = os.path.splitext(file.filename)[1]
            filename = secure_filename('logo' + ext)
            file.save(os.path.join(STATIC_IMG_DIR, filename))
        return redirect(url_for('configuracion'))

    return render_template('configuracion.html', config=config)

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
                'Moneda': config.get('Moneda', ''),
                'Total': str(float(data['Cantidad']) * float(data['PrecioUnitario'])),
                'Forma_Pago': data['Forma_Pago'],
                'Observaciones': data['Observaciones'],
                'tipo': 'compras'
            }

            ruta = os.path.join(DATA_DIR, 'compras.csv')
            nuevo_archivo = not os.path.exists(ruta)
            with open(ruta, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=datos.keys())
                if nuevo_archivo:
                    writer.writeheader()
                writer.writerow(datos)

            url_compras = config.get('URLScript')
            if url_compras:
                r = requests.post(url_compras, json=datos)
                print("📥 Respuesta Google:", r.text)

            return jsonify({'mensaje': 'Guardado correctamente'}), 200
        except Exception as e:
            print("❌ Error en /compras:", e)
            return jsonify({'error': 'Error interno'}), 500

    formas_pago = ["Efectivo", "SINPE", "Tarjeta Cr."]
    return render_template(
        'compras.html',
        formas_pago=formas_pago,
        moneda=config.get('Moneda', '')
    )

@app.route('/datos_formulario')
def datos_formulario():
    return jsonify({
        'proveedores': leer_csv_como_diccionario(os.path.join(DATA_DIR, 'proveedores.csv')),
        'productos': leer_csv_como_diccionario(os.path.join(DATA_DIR, 'productos.csv')),
        'tipos_negocio': leer_lista_simple(os.path.join(DATA_DIR, 'tipos_negocio.csv')),
        'categorias': leer_lista_simple(os.path.join(DATA_DIR, 'categorias.csv')),
        'unidades': leer_lista_simple(os.path.join(DATA_DIR, 'unidades.csv'))
    })

@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    try:
        data = request.form
        nombre = data.get('nombre', '').strip()
        tipo = data.get('tipo_negocio', '').strip()

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
            'Tipo_de_Negocio': tipo,
            'Observaciones': data.get('observaciones', ''),
            'tipo': 'proveedor'
        }

        nuevo_archivo = not os.path.exists(ruta)
        with open(ruta, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=nuevo.keys())
            if nuevo_archivo:
                writer.writeheader()
            writer.writerow(nuevo)

        url_prov = config.get('URLScriptProveedores')
        if url_prov:
            r = requests.post(url_prov, json=nuevo)
            print("📥 Respuesta proveedor:", r.text)

        return jsonify({'mensaje': 'Proveedor guardado'}), 200
    except Exception as e:
        print("❌ Error en nuevo_proveedor:", e)
        return jsonify({'error': 'Error interno'}), 500

@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    try:
        data = request.form
        nombre = data.get('nombre', '').strip()

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

        nuevo_archivo = not os.path.exists(ruta)
        with open(ruta, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=nuevo.keys())
            if nuevo_archivo:
                writer.writeheader()
            writer.writerow(nuevo)

        url_prod = config.get('URLScriptProductos')
        if url_prod:
            r = requests.post(url_prod, json=nuevo)
            print("📥 Respuesta producto:", r.text)

        return jsonify({'mensaje': 'Producto guardado'}), 200
    except Exception as e:
        print("❌ Error en nuevo_producto:", e)
        return jsonify({'error': 'Error interno'}), 500

@app.route('/proveedores')
def proveedores():
    proveedores = leer_csv_como_diccionario(os.path.join(DATA_DIR, 'proveedores.csv'))
    return render_template(
        'proveedores.html',
        proveedores=proveedores
    )

@app.route('/productos')
def productos():
    productos = leer_csv_como_diccionario(os.path.join(DATA_DIR, 'productos.csv'))
    return render_template(
        'productos.html',
        productos=productos
    )

# Rutas nuevas para el resto del menú
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
