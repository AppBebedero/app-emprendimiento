from flask import Blueprint, render_template, request, redirect, url_for
from config_loader import cargar_configuracion

core_bp = Blueprint('core', __name__)

@core_bp.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

@core_bp.route('/manual')
def manual():
    config = cargar_configuracion()
    return render_template('manual.html', config=config)

@core_bp.route('/acerca')
def acerca():
    config = cargar_configuracion()
    return render_template('acerca.html', config=config)

@core_bp.route('/reportes', methods=['GET', 'POST'])
def reportes():
    config = cargar_configuracion()
    # Aquí va tu lógica de reportes
    return render_template('reportes.html', config=config)
