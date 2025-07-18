from flask import Blueprint, render_template
from config_loader import cargar_configuracion
import time

inicio_bp = Blueprint('inicio', __name__)

@inicio_bp.route('/')
def inicio():
    config = cargar_configuracion()
    timestamp = str(int(time.time()))  # evita caché del logo

    logo_url = config.get("LogoURL", "")
    if logo_url:
        logo_url += f"?v={timestamp}"

    return render_template(
        'inicio.html',
        config=config,
        nombre_negocio=config.get("NombreNegocio", "Sistema Gestión Financiera"),
        logo_exists=bool(config.get("LogoURL")),
        logo_url=logo_url,
        color_principal=config.get("ColorPrincipal", "#0d6efd"),
        color_fondo=config.get("ColorFondo", "#ffffff")
    )
