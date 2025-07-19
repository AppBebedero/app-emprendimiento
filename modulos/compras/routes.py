from flask import Blueprint, render_template, request, redirect, url_for, flash
from modulos.compras.services import obtener_compras
from modulos.compras.repository import guardar_compra

compras_bp = Blueprint('compras', __name__, template_folder='templates/compras')

@compras_bp.route('/', methods=['GET'])
def listado_compras():
    compras = obtener_compras()
    return render_template('compras/listado.html', compras=compras)

@compras_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        datos = request.form.to_dict()
        try:
            guardar_compra(datos)
            flash('Compra guardada con éxito', 'success')
            return redirect(url_for('compras.listado_compras'))
        except Exception as e:
            flash(f'Error al guardar: {e}', 'danger')
    return render_template('compras/formulario.html')
