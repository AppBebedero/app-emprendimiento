from flask import Flask, render_template
from config_loader import cargar_configuracion

# Importar blueprints
from modulos.compras import compras_bp
from modulos.inicio import inicio_bp

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(inicio_bp)
app.register_blueprint(compras_bp, url_prefix='/compras')

@app.route('/')
def index():
    config = cargar_configuracion()

    return render_template(
        'inicio.html',
        config=config,
        nombre_negocio=config.get("NombreNegocio", "Sistema Gestión Financiera"),
        logo_exists=bool(config.get("LogoURL")),
        logo_url=config.get("LogoURL", ""),
        color_principal=config.get("ColorPrincipal", "#0d6efd"),
        color_fondo=config.get("ColorFondo", "#f8f9fa")
    )

if __name__ == '__main__':
    app.run(debug=True)
