def obtener_proveedores():
    from modulos.proveedores.repository import lista_proveedores
    return lista_proveedores()
