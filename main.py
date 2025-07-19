from flask import Flask
from config_loader import cargar_configuracion
from modulos.core.routes import core_bp
from modulos.compras.routes import compras_bp
from modulos.proveedores.routes import proveedores_bp
from modulos.productos.routes import productos_bp
from modulos.contabilidad import Accounting  # ← Importa aquí

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'cambia-esta-clave-segura'

    # Cargo configuración
    config = cargar_configuracion()

    # Inyecto las variables de configuración a todas las plantillas
    @app.context_processor
    def inject_config():
        return dict(
            nombre_negocio   = config.get('NombreNegocio', ''),
            logo_exists      = bool(config.get('LogoURL')),
            logo_url         = config.get('LogoURL', ''),
            color_principal  = config.get('ColorPrincipal', '#0d6efd'),
            color_fondo      = config.get('ColorFondo', '#ffffff')
        )

    # Instancio el módulo contable y lo guardo en la app
    app.accounting = Accounting()

    # Registro de blueprints
    app.register_blueprint(core_bp)
    app.register_blueprint(compras_bp,    url_prefix='/compras')
    app.register_blueprint(proveedores_bp, url_prefix='/proveedores')
    app.register_blueprint(productos_bp,   url_prefix='/productos')

    return app

# Para Render/Gunicorn: exporta siempre `app`
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
