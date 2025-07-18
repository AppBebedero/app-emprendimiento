from flask import Flask, render_template
from config_loader import cargar_configuracion

# Importar blueprints
from modulos.compras import compras_bp
from modulos.inicio import inicio_bp

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(inicio_bp)
app.register_blueprint(compras_bp, url_prefix='/compras')  # ← Esta línea es clave

@app.route('/')
def index():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

if __name__ == '__main__':
    app.run(debug=True)
