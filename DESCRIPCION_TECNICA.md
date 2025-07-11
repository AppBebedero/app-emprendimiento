# 📦 App de Control de Compras - Party Box

Esta aplicación fue desarrollada en Flask para registrar compras, proveedores y productos de manera sencilla, con formularios web y almacenamiento en archivos `.csv`. Es totalmente funcional sin necesidad de base de datos externa o login.

---

## 📌 Rutas principales

| Ruta               | Archivo HTML           | Función principal                                                              |
|--------------------|------------------------|---------------------------------------------------------------------------------|
| `/`                | `inicio.html`          | Página de bienvenida con imagen principal                                      |
| `/configuracion`   | `configuracion.html`   | Vista de configuración con datos generales del emprendimiento                  |
| `/compras`         | `compras.html`         | Formulario para registrar compras, incluyendo listas desplegables dinámicas    |
| `/proveedores`     | `proveedores.html`     | Registro de nuevos proveedores con tipo de negocio                             |
| `/productos`       | `productos.html`       | Registro de productos, vinculados a un proveedor ya existente                  |

---

## 📂 Estructura de carpetas

```
├── flask_app.py
├── config_loader.py
├── config.json (si aplica)
├── data/
│   ├── proveedores.csv
│   ├── productos.csv
├── templates/
│   ├── base.html
│   ├── inicio.html
│   ├── configuracion.html
│   ├── compras.html
│   ├── proveedores.html
│   ├── productos.html
├── static/
│   ├── Inicio.png
│   ├── LogoPartyBox.png
```

---

## 📄 Archivos CSV utilizados

### 🔹 `proveedores.csv`

Contiene los datos de los proveedores registrados:

```csv
Nombre,Teléfono,Email,Contacto,Celular,Tipo,Observaciones
```

Notas:
- El campo `Tipo` es una categoría: Librería, Suministros, Servicios, Otros.
- Se utiliza para completar la lista en el formulario de compras y productos.

---

### 🔹 `productos.csv`

Contiene los productos registrados en la app:

```csv
Nombre,Categoría,Unidad,Proveedor,Observaciones
```

Notas:
- El campo `Proveedor` se selecciona de los ya registrados.
- Las unidades pueden ser: Unidad, Litro, Metro, Caja, Bolsa.
- Las categorías incluyen: Bebidas, Alimentos, Limpieza, Tecnología, Otros.

---

## ⚙️ Funcionalidad técnica

- Todas las rutas se encuentran definidas en `flask_app.py`
- Los archivos `.csv` se crean automáticamente en la carpeta `data/` si no existen.
- Se usan formularios HTML con diseño responsive y botones de Guardar/Cancelar.
- Los datos del formulario de compras se envían también a Google Sheets mediante un Web App de Apps Script.
- No requiere conexión a base de datos o login.

---

## 🧠 Posibles mejoras futuras

- Permitir editar o eliminar registros desde una tabla HTML.
- Registrar categorías y unidades desde formularios independientes.
- Generar reportes por rango de fechas o proveedor.
- Agregar autenticación básica para uso empresarial.
- Conectar con Google Sheets también para proveedores y productos, si se desea sincronizar con Drive.

---

## 📝 Notas del desarrollador

Este archivo fue creado como documentación interna para uso de desarrollo y mantenimiento.  
**No se muestra públicamente en la App web.**  
Puede ser actualizado según se agreguen nuevas funcionalidades.

Desarrollado con cariño por José Daniel y ChatGPT ✨
