from flask import Flask, render_template, redirect, request, url_for
from datetime import datetime
from collections import defaultdict
import os

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
                if len(partes) == 12:
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
                        estado = partes[11].strip()
                        pedidos_dict[pid]['estado'] = estado

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

                elif len(partes) >= 8:
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
                        estado = partes[8].strip() if len(partes) > 8 else 'registrado'
                        pedidos_dict[pid]['estado'] = estado
                        
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
    return render_template(
        'registrar_pedido.html',
        exito=exito,
        cedula=request.args.get('cedula', ''),
        nombre=request.args.get('nombre', ''),
        telefono=request.args.get('telefono', ''),
        direccion=request.args.get('direccion', ''),
        cliente_existente=bool(request.args.get('nombre'))
    )


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
    return render_template('lista_pedidos.html', pedidos=pedidos)

@app.route('/detalle_pedido_cliente/<int:pedido_id>')
def detalle_pedido_cliente(pedido_id):
    pedidos = leer_pedidos()
    pedido = next((p for p in pedidos if p['id'] == pedido_id), None)
    if pedido:
        return render_template('detalle_pedido_cliente.html', pedido=pedido, pedido_id=pedido_id)
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

@app.route('/modificar_pedido/<int:pedido_id>', methods=['GET'])
def modificar_pedido(pedido_id):
    pedidos_lista = leer_pedidos()
    pedido = next((p for p in pedidos_lista if p["id"] == pedido_id), None)
    if pedido:
        return render_template('modificar_pedido.html', pedido=pedido, pedido_id=pedido_id)
    else:
        return "Pedido no encontrado", 404
    
@app.route('/editar_producto/<int:pedido_id>/<int:producto_index>', methods=['GET'])
def editar_producto(pedido_id, producto_index):
    pedidos = leer_pedidos()
    pedido = next((p for p in pedidos if p["id"] == pedido_id), None)
    
    if not pedido or producto_index >= len(pedido["productos"]):
        return "Producto o pedido no encontrado", 404
    
    producto = pedido["productos"][producto_index]
    return render_template("editar_producto.html", pedido=pedido, producto=producto, producto_index=producto_index)


@app.route('/actualizar_pedido/<int:pedido_id>', methods=['POST'])
def actualizar_pedido(pedido_id):
    pedidos_lista = leer_pedidos()
    pedido = next((p for p in pedidos_lista if p["id"] == pedido_id), None)
    if not pedido:
        return "Pedido no encontrado", 404

    
    productos = request.form.getlist('producto[]')
    sabores = request.form.getlist('sabor[]')
    cantidades = request.form.getlist('cantidad[]')
    observaciones = request.form.getlist('observaciones[]')

    # actualizar datos del pedido
    nuevos_productos = []
    for p, s, c, o in zip(productos, sabores, cantidades, observaciones):
        nuevos_productos.append({
            "producto": p,
            "sabor": s,
            "cantidad": int(c),
            "observaciones": o
        })

    pedido['productos'] = nuevos_productos
    pedido['nombre'] = request.form['nombre']
    pedido['documento'] = request.form['documento']
    pedido['telefono'] = request.form['telefono']
    pedido['direccion'] = request.form['direccion']
    pedido['forma_entrega'] = request.form['formaEntrega']
    pedido['estado'] = request.form['estado']

    #ahora sobrescribe el archivo
    try:
        with open(ARCHIVO_PEDIDOS, 'w', encoding='utf-8') as f:
            for p in pedidos_lista:
                detalles = "|".join(
                    f"{prod['producto']}-{prod['cantidad']}-{prod['sabor']}-{prod['observaciones']}"
                    for prod in p["productos"]
                )

                estado = p.get('estado', 'Registrado').strip()

                linea = f"{p['id']},{detalles},{p['nombre']},{p['documento']},{p['telefono']},{p['forma_entrega']},{p['direccion']},{p['hora'].strftime('%Y-%m-%d %H:%M:%S')},{estado}\n"
                
                f.write(linea)
    except Exception as e:
        return f"Error al guardar el pedido: {e}", 500

    return redirect(url_for('detalle_pedido_cliente', pedido_id=pedido_id))

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

    return render_template('estado_pedido.html', mensaje=mensaje, clase_color=clase_color, pedido=pedido)

@app.route('/cancelar_pedido/<int:pedido_id>', methods=['POST'])
def cancelar_pedido(pedido_id):
    pedidos = leer_pedidos()
    pedido = next((p for p in pedidos if p['id'] == pedido_id), None)

    if not pedido:
        return "Pedido no encontrado", 404

    estado_actual = pedido.get("estado", "Registrado").lower()

    mensajes_estado = {
        'registrado': "✅ El pedido ha sido cancelado exitosamente. Gracias por avisarnos.",
        
        'preparacion': "⚠️ No se puede cancelar el pedido porque ya está en preparación. Por favor, <a href='/contactanos'><strong>contacta a nuestro servicio al cliente</strong></a> si necesitas más ayuda.",
        
        'listo': "⚠️ Tu pedido ya está listo para ser entregado o recogido. En esta etapa no es posible cancelarlo. <a href='/contactanos'><strong>Contacta al servicio al cliente</strong></a> para mayor asistencia.",
        
        'en camino': "📦 El pedido ya está en camino y no puede ser cancelado. Puedes rechazarlo en el momento de entrega o <a href='/contactanos'><strong>escribirnos aquí</strong></a> para más opciones.",
        
        'entregado': "🚚 El pedido ya fue entregado. Si tienes inconvenientes, por favor <a href='/contactanos'><strong>contacta a nuestro equipo de soporte</strong></a>.",
        
        'cancelado': "ℹ️ Este pedido ya fue cancelado anteriormente. Si fue un error, por favor <a href='/contactanos'><strong>crea uno nuevo o contáctanos</strong></a>.",
    }

    if estado_actual != "registrado":
        mensaje = mensajes_estado.get(estado_actual, "⚠️ No se puede cancelar el pedido debido a un estado desconocido. <a href='/contactanos'><strong>Contáctanos</strong></a> para revisar el caso.")
        return render_template("estado_pedido.html", mensaje=mensaje, clase_color="rojo", pedido=pedido, pedido_id=pedido_id)


    # Cambiar el estado a cancelado
    pedido["estado"] = "cancelado"

    # Guardar los cambios
    try:
        with open(ARCHIVO_PEDIDOS, 'w', encoding='utf-8') as f:
            for p in pedidos:
                detalles = "|".join(
                    f"{prod['producto']}-{prod['cantidad']}-{prod['sabor']}-{prod['observaciones']}"
                    for prod in p["productos"]
                )
                estado = p.get('estado', 'Registrado').strip()
                linea = f"{p['id']},{detalles},{p['nombre']},{p['documento']},{p['telefono']},{p['forma_entrega']},{p['direccion']},{p['hora'].strftime('%Y-%m-%d %H:%M:%S')},{estado}\n"
                f.write(linea)
        mensaje = mensajes_estado['registrado']
        return render_template("estado_pedido.html", mensaje=mensaje, clase_color="verde", pedido=pedido, pedido_id=pedido_id)
    except Exception as e:
        return f"Error al cancelar el pedido: {e}", 500
    
@app.route('/verificar_cliente', methods=['GET', 'POST'])
def verificar_cliente():
    if request.method == 'POST':
        cedula = request.form['cedula']
        nombre = ''
        telefono = ''
        direccion = ''
        encontrado = False

        with open('pedidos.txt', 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                partes = linea.strip().split(',')
                if len(partes) >= 8 and partes[3] == cedula:
                    nombre = partes[2]
                    telefono = partes[4]
                    direccion = partes[6]
                    encontrado = True
                    break

        if encontrado:
            return redirect(url_for('registrar_pedido', cedula=cedula, nombre=nombre, telefono=telefono, direccion=direccion))
        else:
            return redirect(url_for('registrar_pedido', cedula=cedula))  #solo autorellena cédula

    return render_template('verificar_cliente.html')



if __name__ == '__main__':
    # Configuración para Render
    port = int(os.environ.get('PORT', 5000))  
    app.run(debug=True, host='0.0.0.0', port=port)

    # Para desarrollo local, puedes usar:
    #app.run(debug=True, port=5000)  