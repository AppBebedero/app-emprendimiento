from flask import Blueprint, render_template
from config_loader import cargar_configuracion

inicio_bp = Blueprint('inicio', __name__)

@inicio_bp.route('/inicio')
def mostrar_inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)
