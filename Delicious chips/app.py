from flask import Flask, render_template, redirect, request, url_for
from datetime import datetime

app = Flask(__name__)

ARCHIVO_PEDIDOS = 'pedidos.txt'

def leer_pedidos():
    pedidos = []
    try:
        with open(ARCHIVO_PEDIDOS, 'r', encoding='utf-8') as f:
            for linea in f:
                partes = linea.strip().split(',')
                if len(partes) >= 8:
                    producto, cantidad, sabor, observaciones, nombre, documento, telefono, entrega, direccion, hora_str = partes
                    hora = datetime.strptime(hora_str, '%Y-%m-%d %H:%M:%S')
                    pedidos.append({
                        "producto": producto,
                        "cantidad": int(cantidad),
                        "sabor": sabor,
                        "observaciones": observaciones,
                        "nombre": nombre,
                        "documento": documento,
                        "telefono": telefono,
                        "forma_entrega": entrega,
                        "direccion": direccion,
                        "hora": hora
                    })
    except FileNotFoundError:
        pass
    return sorted(pedidos, key=lambda x: x['hora'])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar_pedido')
def registrar_pedido():
    exito = request.args.get('exito')
    return render_template('registrar_pedido.html', exito=exito)

@app.route('/reg_pedido', methods=['POST'])
def reg_pedido():
    producto = request.form['producto']
    cantidad = request.form['cantidad']
    sabor = request.form['sabor']
    observaciones = request.form['observaciones']
    nombre = request.form['nombre']
    documento = request.form['documento']
    telefono = request.form['telefono']
    forma_entrega = request.form['formaEntrega']
    direccion = request.form['direccion']
    hora = datetime.now()
    hora_for = hora.strftime('%Y-%m-%d %H:%M:%S')

    # Guardar en un archivo
    with open(ARCHIVO_PEDIDOS, 'a', encoding='utf-8') as f:
        f.write(
            f"{producto},{cantidad},{sabor},"
            f"{observaciones.capitalize()},{nombre.capitalize()},{documento}, "
            f"{telefono},{forma_entrega.capitalize()},{direccion.capitalize()},{hora_for}\n"
        )
    #facturación
    pedidos = leer_pedidos()
    pedido_id = len(pedidos) - 1
    return redirect(url_for('factura', pedido_id=pedido_id))

@app.route('/pedidos')
def pedidos():
    pedidos = leer_pedidos()
    return render_template('lista_pedidos.html', pedidos=pedidos)

@app.route('/factura/<int:pedido_id>')
def factura(pedido_id):
    pedidos = leer_pedidos()
    if 0 <= pedido_id < len(pedidos):
        pedido = pedidos[pedido_id]
        return render_template('factura.html', pedido=pedido, pedido_index=pedido_id)

    return "Factura no encontrada", 404

if __name__ == '__main__':
    app.run(debug=True)
