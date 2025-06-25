from ver_lista_pedidos import mostrar_lista_pedidos

def ver_detalle_pedido(pedidos):
    if not pedidos:
        print("No hay pedidos disponibles.")
        return
    
    mostrar_lista_pedidos(pedidos)

    try:
        seleccion = int(input("\nIngrese el número del pedido que desea ver: "))
        if 1 <= seleccion <= len(pedidos):
            pedido = pedidos[seleccion - 1]

            print("\nDetalles del pedido seleccionado:")
            print(f"Nombre: {pedido.get('nombre', '').capitalize()}")
            print(f"Producto: {pedido.get('producto', '').capitalize()}")
            print(f"Cantidad: {pedido.get('cantidad', '')}")
            print(f"Sabor: {pedido.get('sabor', '').capitalize()}")
            print(f"Observaciones: {pedido.get('observaciones', '')}")
            print(f"Teléfono: {pedido.get('telefono', '')}")
            print(f"Dirección: {pedido.get('direccion', '').capitalize()}")
            print(f"Forma de entrega: {pedido.get('forma_entrega', '').capitalize()}")

        else:
            print("Selección inválida. Por favor, ingrese un número válido.")
    except ValueError:
        print("Entrada no válida. Por favor, ingrese un número correcto.")

