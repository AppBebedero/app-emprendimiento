from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests, os, csv, json
from werkzeug.utils import secure_filename
from config_loader import cargar_configuracion

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'

# Rutas de disco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_IMG_DIR = os.path.join(BASE_DIR, 'static', 'img')
OVERRIDE_PATH = os.path.join(BASE_DIR, 'config_overrides.json')

# Asegurar directorios
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_IMG_DIR, exist_ok=True)

# Cargar configuración inicial desde Google Sheets
config = cargar_configuracion()

# Cargar overrides locales (logo + color)
overrides = {}
if os.path.exists(OVERRIDE_PATH):
    with open(OVERRIDE_PATH, 'r', encoding='utf-8') as f:
        overrides = json.load(f)
config.update(overrides)

# Helper para subir logo
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                fila[0] for fila in csv.reader(f)
                if fila and fila[0].strip() and fila[0] != 'Seleccione uno'
            ]
    except:
        return []

@app.route('/')
def inicio():
    return render_template('inicio.html', config=config)

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    if request.method == 'POST':
        # 1) Subida de logo
        file = request.files.get('logo')
        if file and allowed_file(file.filename):
            ext = os.path.splitext(file.filename)[1]
            filename = secure_filename('logo' + ext)
            path = os.path.join(STATIC_IMG_DIR, filename)
            file.save(path)
            # Normalizar siempre a logo.png
            if ext.lower() != '.png':
                os.replace(path, os.path.join(STATIC_IMG_DIR, 'logo.png'))

        # 2) Cambio de color principal
        nuevo_color = request.form.get('ColorPrincipal')
        if nuevo_color:
            overrides['ColorPrincipal'] = nuevo_color
            with open(OVERRIDE_PATH, 'w', encoding='utf-8') as f:
                json.dump(overrides, f)
            config['ColorPrincipal'] = nuevo_color

        return redirect(url_for('configuracion'))

    return render_template('configuracion.html', config=config)

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    if request.method == 'POST':
        # ... tu lógica de guardar compras ...
        return jsonify({'mensaje': 'Guardado correctamente'}), 200

    formas_pago = ["Efectivo", "SINPE", "Tarjeta Cr."]
    return render_template('compras.html',
                           formas_pago=formas_pago,
                           moneda=config.get('Moneda', ''))

@app.route('/datos_formulario')
def datos_formulario():
    return jsonify({
        'proveedores': leer_csv_como_diccionario(os.path.join(DATA_DIR,'proveedores.csv')),
        'productos':  leer_csv_como_diccionario(os.path.join(DATA_DIR,'productos.csv')),
        'tipos_negocio': leer_lista_simple(os.path.join(DATA_DIR,'tipos_negocio.csv')),
        'categorias': leer_lista_simple(os.path.join(DATA_DIR,'categorias.csv')),
        'unidades': leer_lista_simple(os.path.join(DATA_DIR,'unidades.csv')),
    })

@app.route('/nuevo_proveedor', methods=['POST'])
def nuevo_proveedor():
    # ... tu lógica actual ...
    return jsonify({'mensaje':'Proveedor guardado'})

@app.route('/nuevo_producto', methods=['POST'])
def nuevo_producto():
    # ... tu lógica actual ...
    return jsonify({'mensaje':'Producto guardado'})

@app.route('/proveedores')
def proveedores():
    datos = leer_csv_como_diccionario(os.path.join(DATA_DIR,'proveedores.csv'))
    return render_template('proveedores.html', proveedores=datos)

@app.route('/productos')
def productos():
    datos = leer_csv_como_diccionario(os.path.join(DATA_DIR,'productos.csv'))
    return render_template('productos.html', productos=datos)

# Rutas adicionales inalteradas: facturación, clientes, costos, finanzas, reportes, manual, acerca

if __name__ == '__main__':
    app.run(debug=True)
