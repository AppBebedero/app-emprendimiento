from flask import Blueprint, render_template, request, jsonify
import os
import csv
import json
from datetime import datetime

compras_bp = Blueprint('compras', __name__, template_folder='templates')

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')

def leer_csv_como_diccionario(ruta):
    with open(ruta, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def leer_lista_simple(ruta):
    with open(ruta, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

@compras_bp.route('/compras')
def vista_compras():
    return render_template('compras.html')

@compras_bp.route('/datos_formulario')
def datos_formulario():
    try:
        return jsonify({
            'proveedores': [p for p in leer_csv_como_diccionario(os.path.join(DATA_DIR, 'proveedores.csv')) if p.get('Nombre')],
            'productos': [p for p in leer_csv_como_diccionario(os.path.join(DATA_DIR, 'productos.csv')) if p.get('Nombre')],
            'formas_pago': leer_lista_simple(os.path.join(DATA_DIR, 'formas_pago.csv')),
            'tipos_compra': leer_lista_simple(os.path.join(DATA_DIR, 'tipos_compra.csv')),
            'unidades': leer_lista_simple(os.path.join(DATA_DIR, 'unidades.csv'))
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@compras_bp.route('/guardar_compra', methods=['POST'])
def guardar_compra():
    datos = request.get_json()
    datos['Total'] = float(datos['Cantidad']) * float(datos['PrecioUnitario'])
    datos['Timestamp'] = datetime.now().isoformat()

    archivo = os.path.join(DATA_DIR, 'compras.csv')
    archivo_existe = os.path.isfile(archivo)

    with open(archivo, 'a', newline='', encoding='utf-8') as f:
        campos = ['Fecha', 'N_Documento', 'Proveedor', 'Producto', 'Cantidad',
                  'PrecioUnitario', 'Moneda', 'Total', 'Forma_Pago', 'Tipo_Compra', 'Observaciones', 'Timestamp']
        writer = csv.DictWriter(f, fieldnames=campos)
        if not archivo_existe:
            writer.writeheader()
        writer.writerow(datos)

    return jsonify({'mensaje': 'Compra guardada correctamente'})
