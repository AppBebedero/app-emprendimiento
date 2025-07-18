from flask import Blueprint, render_template, request, jsonify
from config_loader import cargar_configuracion
from utils.datos_csv import leer_csv_como_diccionario, leer_lista_simple
import os

compras_bp = Blueprint('compras', __name__, template_folder='../templates')

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

@compras_bp.route('/compras')
def mostrar_compras():
    config = cargar_configuracion()
    return render_template('compras.html', config=config)

@compras_bp.route('/datos_formulario')
def datos_formulario():
    try:
        return jsonify({
            'proveedores': [
                p for p in leer_csv_como_diccionario(os.path.join(DATA_DIR, 'proveedores.csv'))
                if p.get('Nombre')
            ],
            'productos': leer_csv_como_diccionario(os.path.join(DATA_DIR, 'productos.csv')),
            'categorias': leer_lista_simple(os.path.join(DATA_DIR, 'categorias.csv')),
            'unidades': leer_lista_simple(os.path.join(DATA_DIR, 'unidades.csv')),
            'tipos_negocio': leer_lista_simple(os.path.join(DATA_DIR, 'tipos_negocio.csv')),
            'tipos_compra': leer_lista_simple(os.path.join(DATA_DIR, 'tipos_compra.csv')),
            'formas_pago': ['Efectivo', 'SINPE', 'Tarjeta Cr.', 'Transferencia']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
