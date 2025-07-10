from flask import Flask, render_template
from config_loader import cargar_configuracion

app = Flask(__name__)
config = cargar_configuracion()

@app.route('/')
def inicio():
    return render_template('inicio.html', config=config)

@app.route('/configuracion')
def configuracion():
    return render_template('configuracion.html', config=config)

if __name__ == '__main__':
    app.run(debug=True)
