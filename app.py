from flask import Flask, render_template, redirect, request, url_for
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

ARCHIVO_PEDIDOS = 'pedidos.txt'

def leer_pedidos():
    pedidos_dict = defaultdict(lambda:{
          
        "productos": [],
        "nombre": "",
        "documento": "",
        "telefono": "",
        "forma_entrega": "",
        "direccion": "",
        "hora": None
    })

    try:
        with open(ARCHIVO_PEDIDOS, 'r', encoding='utf-8') as f:
            
            for linea in f:
                partes = linea.strip().split(',')
                if len(partes) == 11:
                    # un producto por pedido
                    try:
                        pid = int(partes[0])
                        producto = partes[1]
                        cantidad = int(partes[2])
                        sabor = partes[3]
                        observaciones = partes[4]
                        nombre = partes[5]
                        documento = partes[6]
                        telefono = partes[7]
                        forma_entrega = partes[8]
                        direccion = partes[9]
                        hora = datetime.strptime(partes[10], '%Y-%m-%d %H:%M:%S')

                        pedidos_dict[pid].update({
                            "id": pid,
                            "nombre": nombre,
                            "documento": documento,
                            "telefono": telefono,
                            "forma_entrega": forma_entrega,
                            "direccion": direccion,
                            "hora": hora
                        })

                        pedidos_dict[pid]["productos"].append({
                            "producto": producto,
                            "cantidad": cantidad,
                            "sabor": sabor,
                            "observaciones": observaciones
                        })
                    except Exception as e:
                        print(f"⚠️ Error procesando línea (formato viejo): {linea.strip()} | {e}")
                        continue

                elif len(partes) == 8:
                    # mas de un producto por pedido
                    try:
                        pid = int(partes[0])
                        detalles = partes[1]
                        
                        nombre = partes[2]
                        documento = partes[3]
                        telefono = partes[4]
                        forma_entrega = partes[5]
                        direccion = partes[6]
                        hora = datetime.strptime(partes[7], '%Y-%m-%d %H:%M:%S')
                        
                        pedidos_dict[pid].update({
                            "id": pid,
                            "nombre": nombre,
                            "documento": documento,
                            "telefono": telefono,
                            "forma_entrega": forma_entrega,
                            "direccion": direccion,
                            "hora": hora
                        })


                        productos = detalles.split('|')
                        for p in productos:
                            try:
                                producto, cantidad, sabor, observaciones = p.split('-', 3)
                                pedidos_dict[pid]["productos"].append({
                                    "producto": producto,
                                    "cantidad": int(cantidad),
                                    "sabor": sabor,
                                    "observaciones": observaciones
                                })
                            except ValueError:
                                print(f"Error en línea de producto mal formada: '{p}'")
                    except Exception as e:
                        print(f"Error procesando línea (formato nuevo): {linea.strip()} | {e}")
                        continue            
                else:
                    print(f"Línea con formato desconocido: {linea.strip()}")


    except FileNotFoundError:
        print("Archivo no encontrado.")
        return []
    return sorted(pedidos_dict.values(), key=lambda x: x['hora'])

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

    productos = request.form.getlist('producto[]')
    cantidades = request.form.getlist('cantidad[]')
    sabores = request.form.getlist('sabor[]')
    observaciones_list = request.form.getlist('observaciones[]')

    if not (len(productos) == len(cantidades) == len(sabores) == len(observaciones_list)):
        return "Error: los campos de producto no coinciden en cantidad.", 400
    
    nombre = request.form['nombre']
    documento = request.form['documento']
    telefono = request.form['telefono']
    forma_entrega = request.form['formaEntrega']
    direccion = request.form['direccion']
    hora = datetime.now()
    hora_for = hora.strftime('%Y-%m-%d %H:%M:%S')
    
    pedido_id = obtener_nuevo_id()

    detalles = "|".join(
        f"{prod}-{cant}-{sabor}-{obs.strip() if obs.strip() else 'Sin observaciones'}"
        for prod, cant, sabor, obs in zip(productos, cantidades, sabores, observaciones_list)

    )

    linea_pedido = f"{pedido_id},{detalles},{nombre},{documento},{telefono},{forma_entrega},{direccion},{hora_for}\n"

    # Guardar en un archivo
    try:
        with open(ARCHIVO_PEDIDOS, 'a', encoding='utf-8') as f:
            f.write(linea_pedido)
        print("✅ Pedido guardado exitosamente.")
    except Exception as e:
        app.logger.error(f"❌ Error al guardar el pedido: {e}")
        return render_template("error.html", mensaje="Ocurrió un problema al guardar tu pedido. Inténtalo de nuevo.")

    return redirect(url_for('pedido_exitoso', pedido_id=pedido_id))

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
        precio_unitario = 5000
        total = sum(p["cantidad"] * precio_unitario for p in pedido["productos"])
        print("📦 Productos del pedido:", pedido["productos"])

        return render_template('factura.html', pedido=pedido, pedido_index=pedido_id,total=total, precio_unitario=precio_unitario)
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
