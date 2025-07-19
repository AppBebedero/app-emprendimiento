from flask import Blueprint, render_template, request, redirect, url_for, flash
from modulos.productos.services import obtener_productos
from modulos.productos.repository import guardar_producto

productos_bp = Blueprint('productos', __name__, template_folder='templates/productos')

@productos_bp.route('/', methods=['GET'])
def listado_productos():
    productos = obtener_productos()
    return render_template('productos/listado.html', productos=productos)

@productos_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        datos = request.form.to_dict()
        try:
            guardar_producto(datos)
            flash('Producto guardado', 'success')
            return redirect(url_for('productos.listado_productos'))
        except Exception as e:
            flash(f'Error al guardar: {e}', 'danger')
    return render_template('productos/formulario.html')
