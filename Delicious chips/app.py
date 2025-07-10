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
                    pid, producto, cantidad, sabor, observaciones, nombre, documento, telefono, entrega, direccion, hora_str = partes
                    hora = datetime.strptime(hora_str, '%Y-%m-%d %H:%M:%S')
                    pedidos.append({
                        "id": int(pid),
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

def obtener_nuevo_id():
    """
    Genera un nuevo ID secuencial basado en el último ID del archivo de pedidos.
    Si no hay pedidos aún, empieza en 1.
    """
    try:
        with open(ARCHIVO_PEDIDOS, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            if not lineas:
                return 1
            ultima_linea = lineas[-1].strip()
            partes = ultima_linea.split(',')
            if partes and partes[0].isdigit():
                return int(partes[0]) + 1
            else:
                return 1
    except FileNotFoundError:
        return 1

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
    
    pedido_id = obtener_nuevo_id()

    # Guardar en un archivo
    with open(ARCHIVO_PEDIDOS, 'a', encoding='utf-8') as f:
        f.write(
            f"{pedido_id},{producto},{cantidad},{sabor},"
            f"{observaciones.capitalize()},{nombre.capitalize()},{documento}, "
            f"{telefono},{forma_entrega.capitalize()},{direccion.capitalize()},{hora_for}\n"
        )

    return redirect(url_for('pedido_exitoso', pedido_id=pedido_id))
    #return redirect(url_for('registrar_pedido', exito='1', pid=pedido_id))
    #facturación
    #return redirect(url_for('factura', pedido_id=pedido_id))

@app.route('/pedido_exitoso/<int:pedido_id>')
def pedido_exitoso(pedido_id):
    
    return render_template('pedido_exitoso.html', pedido_id=pedido_id)

@app.route('/pedidos')
def pedidos():
    pedidos = leer_pedidos()
    return render_template('lista_pedidos.html', pedidos=enumerate(pedidos))

@app.route('/detalle_pedido_cliente/<int:pedido_id>')
def detalle_pedido_cliente(pedido_id):
    pedidos = leer_pedidos()
    pedido = next((p for p in pedidos if p['id'] == pedido_id), None)
    if pedido:
        return render_template('detalle_pedido_cliente.html', pedido=pedido, pedido_index=pedido_id)
    return "Pedido no encontrado", 404


@app.route('/factura/<int:pedido_id>')
def factura(pedido_id):
    pedidos = leer_pedidos()
    pedido = next((p for p in pedidos if p['id'] == pedido_id), None)
    if pedido:
        return render_template('factura.html', pedido=pedido, pedido_index=pedido_id)
    return "Factura no encontrada", 404

ARCHIVO_CONTACTOS = 'contactos.txt'

@app.route('/contactanos', methods=['GET', 'POST'])
def contactanos():
    if request.method == 'POST':
        nombre = request.form['nombre']
        documento = request.form['documento']
        correo = request.form['correo']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(ARCHIVO_CONTACTOS, 'a', encoding='utf-8') as f:
            f.write(f"{nombre},{documento},{correo},{telefono},{direccion},{hora}\n")

        return render_template('contactanos.html', mensaje="¡Gracias por contactarnos! 😊")

    return render_template('contactanos.html')

@app.route('/estado_pedido')
def estado_pedido():
    return render_template('estado_pedido.html')


@app.route('/ver_estado_pedido', methods=['POST'])
def ver_estado_pedido():
    try:
        numero = int(request.form['numero'])
        pedidos = leer_pedidos()

        pedido = next((p for p in pedidos if p['id'] == numero), None)
        if pedido:
            estado = pedido.get('estado', 'Registrado')
            mensaje = f"📦 El estado actual del pedido #{numero:04d} es: {estado.upper()}"
            clase_color = 'verde'
        else:
            mensaje = "❌ No se encontró el pedido. Verifica el número ingresado."
            clase_color = 'rojo'

    except:
        mensaje = "⚠️ Número inválido. Intenta nuevamente."
        clase_color = 'rojo'

    return render_template('estado_pedido.html', mensaje=mensaje, clase_color=clase_color)

if __name__ == '__main__':
    app.run(debug=True)
