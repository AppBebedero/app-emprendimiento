from flask import Blueprint, render_template
from config_loader import cargar_configuracion

inicio_bp = Blueprint('inicio', __name__)

@inicio_bp.route('/')
def inicio():
    config = cargar_configuracion()

    return render_template(
        'inicio.html',
        config=config,
        nombre_negocio=config.get("NombreNegocio", ""),
        logo_url=config.get("LogoURL", ""),
        logo_exists=bool(config.get("LogoURL")),
        color_principal=config.get("ColorPrincipal", "#0d6efd"),
        color_fondo=config.get("ColorFondo", "#ffffff")
    )
