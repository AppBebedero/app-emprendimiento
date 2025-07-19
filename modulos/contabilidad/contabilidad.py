import os
import csv
from datetime import datetime
from config_loader import cargar_configuracion

class Accounting:
    def __init__(self):
        # Carga rutas desde configuración (config.json o CSV)
        config = cargar_configuracion()
        self.plan_path = config.get('PlanDeCuentasCSV', 'data/plan_de_cuentas.csv')
        self.journal_path = config.get('JournalCSV', 'data/journal_entries.csv')
        self._ensure_journal()

    def _ensure_journal(self):
        # Crea el archivo de diario si no existe, con cabecera
        if not os.path.exists(self.journal_path):
            os.makedirs(os.path.dirname(self.journal_path), exist_ok=True)
            with open(self.journal_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Fecha',
                    'CuentaDébito',
                    'Débito',
                    'CuentaCrédito',
                    'Crédito',
                    'Descripción',
                    'Referencia'
                ])

    def record_purchase(self, fecha, monto, forma_pago, descripcion='', referencia=''):
        """
        Asiento de compra:
         - Debe: Compras
         - Haber: según forma de pago
        """
        cuenta_debito = 'Compras'
        cuenta_credito = {
            'Efectivo':       'Caja y Bancos',
            'SINPE':          'Caja y Bancos',
            'Tarjeta Cr.':    'Tarjetas por Pagar'
        }.get(forma_pago, 'Proveedores')
        self._write_entry(fecha, cuenta_debito, monto, cuenta_credito, monto, descripcion, referencia)

    def record_sale(self, fecha, monto, forma_pago, descripcion='', referencia=''):
        """
        Asiento de venta:
         - Debe: según forma de pago
         - Haber: Ventas
        """
        cuenta_credito = 'Ventas'
        cuenta_debito = {
            'Efectivo':       'Caja y Bancos',
            'SINPE':          'Caja y Bancos',
            'Tarjeta Cr.':    'Clientes'
        }.get(forma_pago, 'Clientes')
        self._write_entry(fecha, cuenta_debito, monto, cuenta_credito, monto, descripcion, referencia)

    def _write_entry(self, fecha, c_deb, deb, c_cred, cred, desc, ref):
        # Formatea fecha y agrega línea al diario
        fecha_str = fecha.strftime('%Y-%m-%d') if isinstance(fecha, datetime) else fecha
        with open(self.journal_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([fecha_str, c_deb, deb, c_cred, cred, desc, ref])
