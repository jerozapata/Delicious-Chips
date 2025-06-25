
def mostrar_lista_pedidos(pedidos):
    if not pedidos:
        print("No hay pedidos registrados.")
        return

    print("Lista de pedidos por gestionar:\n")
    for i, pedido in enumerate(pedidos, start=1):
        nombre = pedido.get('nombre', '').capitalize()
        producto = pedido.get('producto', '').capitalize()
        cantidad = pedido.get('cantidad', '')
        forma = pedido.get('forma_entrega', '').capitalize()

        print(f"{i}. {nombre} - {producto} x{cantidad} - Entrega: {forma}")

    print(f"Total de pedidos: {len(pedidos)}")