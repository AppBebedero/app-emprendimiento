from flask import Flask
from config_loader import cargar_configuracion
from modulos.inicio import inicio_bp

# Crear la app
app = Flask(__name__)
app.secret_key = "clave-secreta"

# Cargar configuración global
config = cargar_configuracion()

# Registrar Blueprints (módulos)
app.register_blueprint(inicio_bp)

# Ruta raíz (redirige a Inicio)
@app.route('/')
def index():
    return inicio_bp.send_static_file('index.html')

# Ejecutar app
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10000)
