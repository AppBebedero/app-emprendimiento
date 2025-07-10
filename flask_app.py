from flask import Flask, render_template, request, redirect
from config_loader import cargar_configuracion
import pandas as pd
import requests

app = Flask(__name__)

@app.route('/')
def inicio():
    config = cargar_configuracion()
    return render_template('inicio.html', config=config)

@app.route('/configuracion')
def configuracion():
    config = cargar_configuracion()
    return render_template('configuracion.html', config=config)

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    config = cargar_configuracion()
    url_proveedores = config.get('URLProveedores', '')
    url_productos = config.get('URLProductos', '')
    url_script = 'https://script.google.com/macros/s/AKfycbzTTyQcKoFtPyqniEfbtUXbi9XQgzHjl_fl4mJvGT4Wq2_93s3hlZPlQ9U5efruNhRr/exec'

    if request.method == 'POST':
        datos = {
            'Fecha': request.form['Fecha'],
            'N_Documento': request.form['N_Documento'],
            'Proveedor': request.form['Proveedor'],
            'Producto': request.form['Producto'],
            'Cantidad': request.form['Cantidad'],
            'PrecioUnitario': request.form['PrecioUnitario'],
            'Moneda': request.form['Moneda'],
            'Total': float(request.form['Cantidad']) * float(request.form['PrecioUnitario']),
            'Forma_Pago': request.form['Forma_Pago'],
            'Observaciones': request.form['Observaciones']
        }

        try:
            respuesta = requests.post(url_script, json=datos)
            print("📥 Respuesta del script:", respuesta.text)
        except Exception as e:
            print("❌ Error al enviar datos:", e)

        return redirect('/compras')

    proveedores = []
    productos = []

    try:
        df_prov = pd.read_csv(url_proveedores)
        proveedores = df_prov.iloc[:, 0].dropna().tolist()
    except Exception as e:
        print("⚠️ Error cargando proveedores:", e)

    try:
        df_prod = pd.read_csv(url_productos)
        productos = df_prod.iloc[:, 0].dropna().tolist()
    except Exception as e:
        print("⚠️ Error cargando productos:", e)

    return render_template('compras.html', config=config,
                           proveedores=proveedores,
                           productos=productos)

if __name__ == '__main__':
    app.run(debug=True)

