from flask import Flask, render_template
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

@app.route('/pedidos')
def pedidos():
    pedidos = leer_pedidos()
    return render_template('lista_pedidos.html', pedidos=pedidos)

if __name__ == '__main__':
    app.run(debug=True)
