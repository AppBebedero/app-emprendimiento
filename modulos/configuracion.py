from flask import Blueprint, render_template, request, jsonify
from config_loader import cargar_configuracion
import requests

configuracion_bp = Blueprint('configuracion', __name__)

@configuracion_bp.route('/configuracion', methods=['GET'])
def configuracion():
    config = cargar_configuracion()
    return render_template(
        'configuracion.html',
        config=config,
        nombre_negocio=config.get("NombreNegocio", "Mi Negocio"),
        logo_exists=bool(config.get("LogoURL")),
        logo_url=config.get("LogoURL", ""),
        color_principal=config.get("ColorPrincipal", "#0d6efd"),
        color_fondo=config.get("ColorFondo", "#ffffff")
    )

@configuracion_bp.route('/configuracion', methods=['POST'])
def guardar_configuracion():
    try:
        datos = request.get_json()
        url_script = cargar_configuracion().get("URLScriptConfig")

        if not url_script:
            return jsonify({"error": "URLScriptConfig no definida"}), 400

        response = requests.post(url_script, json=datos)
        response.raise_for_status()
        return jsonify({"mensaje": "Configuración guardada correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
