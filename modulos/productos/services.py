def obtener_productos():
    from modulos.productos.repository import lista_productos
    return lista_productos()
