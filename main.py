from flask import Flask
from config_loader import cargar_configuracion
from modulos.core.routes import core_bp
from modulos.compras.routes import compras_bp
from modulos.proveedores.routes import proveedores_bp
from modulos.productos.routes import productos_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'cambia-esta-clave-segura'

    # Cargo la configuración (una sola vez por petición)
    config = cargar_configuracion()

    @app.context_processor
    def inject_config():
        return dict(config=config)

    # Registro de módulos (blueprints)
    app.register_blueprint(core_bp)
    app.register_blueprint(compras_bp, url_prefix='/compras')
    app.register_blueprint(proveedores_bp, url_prefix='/proveedores')
    app.register_blueprint(productos_bp, url_prefix='/productos')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
