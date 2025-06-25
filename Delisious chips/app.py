from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

@app.route('/')
def index():
    exito = request.args.get('exito')
    return render_template('index.html', exito=exito)

@app.route('/regPedido')
def regPedido():
    return render_template('regPedido.html')

@app.route('/registrar_pedido', methods=['POST'])
def registrar_pedido():
    producto = request.form['producto']
    cantidad = request.form['cantidad']
    sabor = request.form['sabor']
    observaciones = request.form['observaciones']
    nombre = request.form['nombre']
    documento = request.form['documento']
    telefono = request.form['telefono']
    forma_entrega = request.form['formaEntrega']
    direccion = request.form['direccion']

    # Guardar en un archivo
    with open('pedidos.txt', 'a', encoding='utf-8') as f:
        f.write(
            f"Producto: {producto}, Cantidad: {cantidad}, Sabor: {sabor}, "
            f"Observaciones: {observaciones}, Nombre: {nombre}, Documento: {documento}, "
            f"Teléfono: {telefono}, Forma de entrega: {forma_entrega}, Dirección: {direccion}\n"
        )

    return redirect(url_for('index', exito=1))

if __name__ == '__main__':
    app.run(debug=True)