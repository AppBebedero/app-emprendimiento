from flask import Flask, render_template, request, redirect, jsonify
import os
import csv
import requests
from config_loader import cargar_configuracion

app = Flask(__name__)

# Asegurar carpeta local
os.makedirs("data", exist_ok=True)

@app.route("/")
def inicio():
    config = cargar_configuracion()
    return render_template("inicio.html", config=config)

@app.route("/reportes")
def reportes():
    config = cargar_configuracion()
    return render_template("reportes.html", config=config)

@app.route("/acerca")
def acerca():
    config = cargar_configuracion()
    return render_template("acerca.html", config=config)

@app.route("/manual")
def manual():
    config = cargar_configuracion()
    return render_template("manual.html", config=config)

@app.route("/verificar_clave", methods=["POST"])
def verificar_clave():
    clave_ingresada = request.form["clave"]
    config = cargar_configuracion()
    clave_correcta = config.get("ClaveAcceso", "")
    if clave_ingresada == clave_correcta:
        return redirect("/reportes")
    return "Clave incorrecta"

@app.route("/configuracion", methods=["GET", "POST"])
def configuracion():
    config = cargar_configuracion()

    if request.method == "POST":
        # 1. Obtener datos del formulario
        nombre_negocio = request.form.get("nombre_negocio", "")
        color = request.form.get("color", "")
        color_fondo = request.form.get("color_fondo", "")
        logo_base64 = request.form.get("logo_base64", "")

        # 2. Preparar datos a enviar
        datos = {
            "NombreNegocio": nombre_negocio,
            "ColorPrincipal": color,
            "ColorFondo": color_fondo,
            "LogoBase64": logo_base64
        }

        # 3. Enviar al Apps Script (URL actualizada)
        url_script = config.get("URLScriptConfig", "")
        try:
            respuesta = requests.post(url_script, json=datos)
            print("📥 Respuesta del script:", respuesta.text)
            return jsonify({"mensaje": "Configuración guardada correctamente."})
        except Exception as e:
            print("❌ Error al guardar configuración:", e)
            return jsonify({"error": "Error al guardar configuración."}), 500

    # GET
    return render_template("configuracion.html", config=config)

if __name__ == "__main__":
    app.run(debug=True)
