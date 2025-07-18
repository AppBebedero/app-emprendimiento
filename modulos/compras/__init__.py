from flask import Blueprint, render_template, jsonify

compras_bp = Blueprint('compras', __name__, template_folder='../../templates')

@compras_bp.route('/')
def mostrar_formulario_compras():
    return render_template('compras.html')

@compras_bp.route('/datos_formulario')
def datos_formulario():
    datos = {
        "proveedores": [{"Nombre": "Proveedor 1"}, {"Nombre": "Proveedor 2"}],
        "productos": [{"Nombre": "Producto A"}, {"Nombre": "Producto B"}],
        "tipos_compra": ["Contado", "Crédito"],
        "formas_pago": ["Efectivo", "SINPE", "Tarjeta Cr."]
    }
    return jsonify(datos)
