from flask import Flask, render_template
from config_loader import cargar_configuracion

# Importar blueprints
from modulos.compras import compras_bp
from modulos.compras.inicio import inicio_bp  # Este depende de si inicio.py existe y tiene un blueprint válido

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(inicio_bp)
app.register_blueprint(compras_bp)

# Ruta principal
@app.route('/')
def index():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

# Ejecutar la app si se corre localmente
if __name__ == '__main__':
    app.run(debug=True)
