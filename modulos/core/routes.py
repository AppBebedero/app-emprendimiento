# modulos/core/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from config_loader import cargar_configuracion
import requests

core_bp = Blueprint('core', __name__, template_folder='templates')

@core_bp.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

@core_bp.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    config = cargar_configuracion()
    # URL de tu Apps Script para guardar configuración
    url_script = config.get('URLScriptConfig', '')

    if request.method == 'POST':
        # Capturo los datos del formulario
        nombre_negocio = request.form['NombreNegocio']
        color_principal = request.form['ColorPrincipal']
        color_fondo = request.form['ColorFondo']
        # Para el logo subido (si hay), tomo el archivo y lo envío como Base64
        logo = request.files.get('LogoArchivo')
        files = {}
        if logo:
            files['LogoArchivo'] = (logo.filename, logo.read(), logo.mimetype)

        # Preparo payload
        payload = {
            'NombreNegocio': nombre_negocio,
            'ColorPrincipal': color_principal,
            'ColorFondo': color_fondo
        }

        try:
            # Envío a tu Apps Script
            if files:
                requests.post(url_script, data=payload, files=files)
            else:
                requests.post(url_script, json=payload)
            flash('Configuración guardada correctamente.', 'success')
        except Exception:
            flash('Error al guardar configuración.', 'danger')

        return redirect(url_for('core.configuracion'))

    # GET: muestro el formulario ya cargado con los valores actuales
    return render_template('configuracion.html', config=config)
