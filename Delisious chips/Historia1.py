import tkinter as tk
from tkinter import messagebox

# Función que valida y registra el pedido
def registrar_pedido(pedido):
    campos_obligatorios = ['producto', 'cantidad', 'sabor', 'nombre', 'telefono', 'direccion', 'observaciones']
    faltantes = []

    for campo in campos_obligatorios:
        if campo not in pedido or not pedido[campo]:
            faltantes.append(campo)

    if faltantes:
        messagebox.showerror("Error", f"Faltan los siguientes campos obligatorios:\n" + "\n".join(faltantes))
        return False
    else:
        resumen = f"Pedido registrado exitosamente.\n\nResumen del pedido:\n\n"
        resumen += f"Producto: {pedido['producto'].capitalize()}\n"
        resumen += f"Cantidad: {pedido['cantidad'].capitalize()}\n"
        resumen += f"Sabor: {pedido['sabor'].capitalize()}\n"
        resumen += f"Observaciones: {pedido['observaciones'].capitalize()}\n"
        resumen += f"Nombre: {pedido['nombre'].capitalize()}\n"
        resumen += f"Teléfono: {pedido['telefono'].capitalize()}\n"
        resumen += f"Dirección: {pedido['direccion'].capitalize()}"
        messagebox.showinfo("Registro Exitoso", resumen)
        return True
    
    

# Función que recoge los datos de los campos y llama a registrar_pedido

pedidos = []    #Lista donde quedarán guardados todos los pedidos

def ejecutar_registro():
    pedido = {
        "producto": entry_producto.get(),
        "cantidad": entry_cantidad.get(),
        "sabor": entry_sabor.get(),
        "nombre": entry_nombre.get(),
        "telefono": entry_telefono.get(),
        "direccion": entry_direccion.get(),
        "observaciones": entry_observaciones.get()
    }
    registrar_pedido(pedido)
    
    pedidos.append(pedido)
    for campo, valor in pedido.items():
        print(f"{campo.capitalize()}: {valor.capitalize()}")


if __name__ == "__main__":
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Registro de Pedido")

    # Etiquetas y campos de entrada
    tk.Label(root, text="Producto").grid(row=0, column=0, padx=10, pady=5)
    entry_producto = tk.Entry(root)
    entry_producto.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Cantidad").grid(row=1, column=0, padx=10, pady=5)
    entry_cantidad = tk.Entry(root)
    entry_cantidad.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="Sabor").grid(row=2, column=0, padx=10, pady=5)
    entry_sabor = tk.Entry(root)
    entry_sabor.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(root, text="Nombre").grid(row=3, column=0, padx=10, pady=5)
    entry_nombre = tk.Entry(root)
    entry_nombre.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(root, text="Teléfono").grid(row=4, column=0, padx=10, pady=5)
    entry_telefono = tk.Entry(root)
    entry_telefono.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(root, text="Dirección").grid(row=5, column=0, padx=10, pady=5)
    entry_direccion = tk.Entry(root)
    entry_direccion.grid(row=5, column=1, padx=10, pady=5)

    tk.Label(root, text="Observaciones").grid(row=6, column=0, padx=10, pady=5)
    entry_observaciones = tk.Entry(root)
    entry_observaciones.grid(row=6, column=1, padx=10, pady=5)

    # Botón para registrar el pedido
    btn_registrar = tk.Button(root, text="Registrar Pedido", command=ejecutar_registro)
    btn_registrar.grid(row=7, column=0, columnspan=2, pady=20)

    # Iniciar la interfaz gráfica
    root.mainloop()