from flask import Blueprint, render_template, request, redirect, url_for, flash
from modulos.proveedores.services import obtener_proveedores
from modulos.proveedores.repository import guardar_proveedor

proveedores_bp = Blueprint('proveedores', __name__, template_folder='templates/proveedores')

@proveedores_bp.route('/', methods=['GET'])
def listado_proveedores():
    proveedores = obtener_proveedores()
    return render_template('proveedores/listado.html', proveedores=proveedores)

@proveedores_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        datos = request.form.to_dict()
        try:
            guardar_proveedor(datos)
            flash('Proveedor guardado', 'success')
            return redirect(url_for('proveedores.listado_proveedores'))
        except Exception as e:
            flash(f'Error al guardar: {e}', 'danger')
    return render_template('proveedores/formulario.html')
