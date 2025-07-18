from flask import Blueprint, render_template
from config_loader import cargar_configuracion

configuracion_bp = Blueprint('configuracion', __name__)

@configuracion_bp.route('/configuracion')
def configuracion():
    config = cargar_configuracion()

    return render_template(
        'configuracion.html',
        config=config,
        nombre_negocio=config.get("NombreNegocio", "Sistema Gestión Financiera"),
        logo_exists=bool(config.get("LogoURL")),
        logo_url=config.get("LogoURL", ""),
        color_principal=config.get("ColorPrincipal", "#0d6efd"),
        color_fondo=config.get("ColorFondo", "#f8f9fa")
    )
