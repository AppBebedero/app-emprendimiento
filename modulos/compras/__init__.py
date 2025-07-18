from flask import Blueprint, render_template

compras_bp = Blueprint('compras', __name__, template_folder='templates')

@compras_bp.route('/')
def mostrar_formulario_compras():
    return render_template('compras.html')

