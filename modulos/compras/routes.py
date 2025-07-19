# modulos/compras/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from config_loader import cargar_configuracion
import requests

# Definimos el blueprint de Compras
compras_bp = Blueprint('compras', __name__, template_folder='templates')

@compras_bp.route('/', methods=['GET', 'POST'])
def compras():
    # Cargo la configuración (URLs, colores, etc.)
    config = cargar_configuracion()
    url_script = config.get('URLScript', '')

    if request.method == 'POST':
        # Capturo los datos del formulario
        fecha         = request.form['Fecha']
        n_doc         = request.form['N_Documento']
        proveedor     = request.form['Proveedor']
        producto      = request.form['Producto']
        cantidad      = request.form['Cantidad']
        precio_unit   = request.form['PrecioUnitario']
        total         = request.form['Total']
        forma_pago    = request.form['Forma_Pago']
        observaciones = request.form.get('Observaciones', '')

        # Envío los datos a Google Sheets (Apps Script)
        payload = {
            'Fecha': fecha,
            'N_Documento': n_doc,
            'Proveedor': proveedor,
            'Producto': producto,
            'Cantidad': cantidad,
            'PrecioUnitario': precio_unit,
            'Total': total,
            'Forma_Pago': forma_pago,
            'Observaciones': observaciones
        }
        try:
            requests.post(url_script, json=payload)
        except Exception:
            flash('Error al guardar en Google Sheets.', 'danger')
            return redirect(url_for('compras.compras'))

        # Registro el asiento contable de la compra
        try:
            current_app.accounting.record_purchase(
                fecha=fecha,
                monto=float(total),
                forma_pago=forma_pago,
                descripcion=f"Compra N° {n_doc}",
                referencia=n_doc
            )
        except Exception:
            flash('Error al generar asiento contable.', 'danger')
            return redirect(url_for('compras.compras'))

        flash('Compra registrada correctamente.', 'success')
        return redirect(url_for('compras.compras'))

    # Si es GET, muestro el formulario
    return render_template('compras.html', config=config)
