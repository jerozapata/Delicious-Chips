from flask import Flask, render_template, redirect, request, url_for, session
from datetime import datetime
from collections import defaultdict
import os
from models import db, Pedido, Producto, Cliente, DetallePedido, Contacto
from dotenv import load_dotenv
import pytz
from flask_migrate import Migrate


now_col = datetime.now(pytz.timezone("America/Bogota"))


load_dotenv()

app = Flask(__name__, instance_relative_config=True)

app.secret_key = 'clave-secreta-delicious'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

USUARIO_ADMIN= 'admin'
PASSWORD_ADMIN= 'papas123'

db.init_app(app)

migrate = Migrate(app, db)


def leer_pedidos():
    
    pedidos = Pedido.query.all()
    resultado = []

    for pedido in pedidos:
        cliente = pedido.cliente
        productos = []

        for detalle in pedido.detalles:
            producto = detalle.producto
            productos.append({
                'producto': producto.nombre,
                'sabor': producto.sabor,
                'gramaje': producto.gramaje,
                'cantidad': detalle.cantidad,
                'precio_unitario': producto.precio_unitario,
                'observaciones': detalle.observaciones or 'Sin observaciones'
            })
        
        resultado.append({
            'id': pedido.id,
            'nombre': cliente.nombre,
            'documento': cliente.documento,
            'telefono': cliente.telefono,
            'email': cliente.email,
            'direccion': cliente.direccion,
            'forma_entrega': pedido.forma_entrega,
            'hora': pedido.fecha_hora,
            'estado': pedido.estado,
            'productos': productos
        })

    return sorted(resultado, key=lambda x: x['hora'])
   

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['username']
        contrasena = request.form['password']
        if usuario == USUARIO_ADMIN and contrasena == PASSWORD_ADMIN:
            session['admin'] = True
            return redirect(url_for('pedidos'))
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    return render_template('admin.html')  # Aquí va tu sección admin real

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))


@app.route('/verificar_cliente', methods=['GET', 'POST'])
def verificar_cliente():

    if request.method == 'POST':
        cedula = request.form['cedula']
        cliente = Cliente.query.filter_by(documento=cedula).first()

        if cliente:
            return redirect(url_for(
                'registrar_pedido',
                cedula=cliente.documento,
                nombre=cliente.nombre,
                telefono=cliente.telefono,
                email = cliente.email,
                direccion=cliente.direccion
            ))
        else:
            return redirect(url_for('registrar_pedido', cedula=cedula))
        
    return render_template('verificar_cliente.html')

@app.route('/registrar_pedido')
def registrar_pedido():

    productos = Producto.query.all()

    return render_template(
        'registrar_pedido.html',
        productos=productos,
        exito=request.args.get('exito'),
        cedula=request.args.get('cedula', ''),
        nombre=request.args.get('nombre', ''),
        telefono=request.args.get('telefono', ''),
        email = request.args.get('email', ''),
        direccion=request.args.get('direccion', ''),
        cliente_existente=bool(request.args.get('nombre'))
    )

@app.route('/reg_pedido', methods=['GET','POST'])
def reg_pedido():

    productos = request.form.getlist('producto[]')
    print("Productos recibidos:", productos)

    
    producto_info = []
    for i, p in enumerate(productos):
        partes = p.split('|')
        if len(partes) != 4:
            print(f"❌ Error en producto[{i}]: '{p}'")
            return f"Error: el producto #{i+1} no tiene el formato esperado.", 400
        producto_info.append(partes)


    cantidades = request.form.getlist('cantidad[]')
    
    observaciones_list = request.form.getlist('observaciones[]')
    


    if not (len(productos) == len(cantidades) == len(observaciones_list)):
        return "Error: los campos de producto no coinciden en cantidad.", 400
    
    nombre = request.form['nombre']
    documento = request.form['documento']
    telefono = request.form['telefono']
    email = request.form['email']
    forma_entrega = request.form['forma_entrega']
    direccion = request.form['direccion']

    productos_list = []
    for (nombre_prod, sabor, gramaje, precio_unitario), cant, obs in zip(producto_info, cantidades, observaciones_list):
        producto = Producto.query.filter_by(nombre=nombre_prod, sabor=sabor, gramaje=gramaje).first()
        productos_list.append({
            'producto': nombre_prod if producto is None else producto.nombre,
            'sabor': sabor,
            'gramaje': gramaje,
            'precio_unitario': precio_unitario,
            'cantidad': int(cant),
            'observaciones': obs.strip() or 'Sin observaciones'
        })

    pedido = {
        'nombre': nombre,
        'documento': documento,
        'telefono': telefono,
        'email': email,
        'forma_entrega': forma_entrega,
        'direccion': direccion,
        'productos': productos_list
    }
    
    return render_template('confirmacion_pedido.html', pedido=pedido, productos=pedido['productos'])

@app.route('/confirmar_pedido', methods=['POST'])
def confirmar_pedido():

    from models import Pedido, Cliente, Producto, DetallePedido

    productos = request.form.getlist('producto[]')
    producto_info = []
    for i, p in enumerate(productos):
        partes = p.split('|')
        if len(partes) != 4:
            print(f"❌ Error en producto[{i}]: '{p}'")
            return f"Error: el producto #{i+1} no tiene el formato esperado.", 400
        producto_info.append(partes)

    cantidades = request.form.getlist('cantidad[]')
    
    observaciones_list = request.form.getlist('observaciones[]')


    nombre = request.form['nombre']
    documento = request.form['documento']
    telefono = request.form['telefono']
    email = request.form['email']
    forma_entrega = request.form['forma_entrega']
    direccion = request.form['direccion']

    
    cliente = Cliente.query.filter_by(documento=documento).first()
    if not cliente:
        cliente = Cliente(nombre=nombre, documento=documento, telefono=telefono, direccion=direccion, email=email)
    
        db.session.add(cliente)
        db.session.commit()


    zona_colombia = pytz.timezone("America/Bogota")
    ahora = datetime.now(zona_colombia).replace(tzinfo=None)


    pedido=Pedido(
        cliente_id=cliente.id,
        forma_entrega=forma_entrega,
        estado='registrado',
        fecha_hora=ahora    
    )
    db.session.add(pedido)
    db.session.commit()

    for (nombre, sabor, gramaje, _), cant, obs in zip(producto_info, cantidades, observaciones_list):

        producto = Producto.query.filter(
            db.func.lower(Producto.nombre) == nombre.strip().lower(),
            db.func.lower(Producto.sabor) == sabor.strip().lower(),
            db.func.lower(Producto.gramaje) == gramaje.strip().lower(),
        ).first()

        if producto:
            print(f"✅ Producto encontrado: {producto.nombre}, {producto.sabor}, {producto.gramaje}")
            detalle = DetallePedido(
                pedido_id=pedido.id,
                producto_id=producto.id,
                cantidad=int(cant),
                observaciones=obs.strip() or 'Sin observaciones'
            )
            db.session.add(detalle)
        else:
            print(f"❌ Producto NO encontrado: {nombre}, {sabor}, {gramaje}")
        
        
        
        
    db.session.commit()
    for d in pedido.detalles:
        print(f"✅ Guardado: {d.producto.nombre}, {d.producto.sabor}, {d.producto.gramaje}, Cant: {d.cantidad}")

    return redirect(url_for('pedido_exitoso', pedido_id=pedido.id))



@app.route('/detalle_pedido/<int:pedido_id>')
def detalle_pedido_cliente(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        return "Pedido no encontrado", 404

    cliente = pedido.cliente
    productos = []
    for detalle in pedido.detalles:
        producto = detalle.producto
        productos.append({
            'producto': producto.nombre,
            'sabor': producto.sabor,
            'gramaje': producto.gramaje,
            'cantidad': detalle.cantidad,
            'observaciones': detalle.observaciones or 'Sin observaciones'
        })

    pedido_dict = {
        'id': pedido.id,
        'nombre': cliente.nombre,
        'documento': cliente.documento,
        'telefono': cliente.telefono,
        'email': cliente.email,
        'direccion': cliente.direccion,
        'forma_entrega': pedido.forma_entrega,
        'estado': pedido.estado,
        'productos': productos,
        'hora': pedido.fecha_hora
    }

    return render_template('detalle_pedido_cliente.html', pedido=pedido_dict, pedido_id=pedido_id)


@app.route('/pedido_exitoso/<int:pedido_id>')
def pedido_exitoso(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    return render_template('pedido_exitoso.html', pedido_id=pedido.id)
    
    
    

@app.route('/pedidos')
def pedidos():
    from models import Pedido
    if not session.get('admin'):
        return redirect(url_for('login'))

    pedidos = leer_pedidos() 
    estado = request.args.get('estado', '').strip().lower()
    fecha_str = request.args.get('fecha', '').strip()
    orden = request.args.get('orden', 'asc')


    query = Pedido.query

    if estado:
        query = query.filter(Pedido.estado.ilike(estado))  # Ignora mayúsculas

    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            # Comparamos solo la parte de fecha (ignoramos hora)
            query = query.filter(db.func.date(Pedido.fecha_hora) == fecha)
        except ValueError:
            pass  # Fecha inválida, no filtramos

    if orden == 'desc':
        query = query.order_by(Pedido.fecha_hora.desc())
    else:
        query = query.order_by(Pedido.fecha_hora.asc())

    pedidos = query.all()

    return render_template('lista_pedidos.html', pedidos=pedidos)

@app.route('/factura/<int:pedido_id>')
def factura(pedido_id):
    from models import Pedido, DetallePedido, Producto

    pedido = db.session.get(Pedido, pedido_id)
    detalles = DetallePedido.query.filter_by(pedido_id=pedido_id).all()

    productos = []
    total = 0

    for d in detalles:
        producto = Producto.query.get(d.producto_id)
        precio_unitario = producto.precio_unitario  # asegúrate de que exista
        subtotal = precio_unitario * d.cantidad
        total += subtotal
        

        productos.append({
            'producto': producto.nombre,
            'sabor': producto.sabor,
            'gramaje': producto.gramaje,
            'cantidad': d.cantidad,
            'precio_unitario': precio_unitario,
            'subtotal': subtotal,
            'observaciones': d.observaciones
        })

    
    return render_template('factura.html',
                           pedido=pedido,
                           productos=productos,
                           total=total)

   

@app.route('/contactanos', methods=['GET', 'POST'])
def contactanos():

    if request.method == 'POST':
        nombre = request.form['nombre']
        documento = request.form['documento']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        mensaje = request.form['mensaje']

        nuevo_contacto = Contacto(
            nombre=nombre,
            documento=documento,
            email=email,
            telefono=telefono,
            direccion=direccion,
            mensaje=mensaje
        )
        db.session.add(nuevo_contacto)
        db.session.commit()

        return render_template('contactanos.html', mensaje="¡Gracias por contactarnos! 😊")

    return render_template('contactanos.html')

      
@app.route('/modificar_pedido/<int:pedido_id>', methods=['GET'])
def modificar_pedido(pedido_id):

    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        return "Pedido no encontrado", 404
    
    cliente = pedido.cliente
    productos = []
    for detalle in pedido.detalles:
        producto = detalle.producto
        productos.append({
            'producto': producto.nombre,
            'sabor': producto.sabor,
            'cantidad': detalle.cantidad,
            'observaciones': detalle.observaciones or 'Sin observaciones'
        })

    pedido_dict = {
        'id': pedido.id,
        'nombre': cliente.nombre,
        'documento': cliente.documento,
        'telefono': cliente.telefono,
        'email': cliente.email,
        'direccion': cliente.direccion,
        'forma_entrega': pedido.forma_entrega,
        'estado': pedido.estado,
        'productos': productos,
        'hora': pedido.fecha_hora
    }
    return render_template('modificar_pedido.html', pedido=pedido_dict, pedido_id=pedido_id)



@app.route('/actualizar_pedido/<int:pedido_id>', methods=['POST'])
def actualizar_pedido(pedido_id):

    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        return "Pedido no encontrado", 404
    
    cliente = pedido.cliente
    cliente.nombre = request.form['nombre']
    cliente.documento = request.form['documento']
    cliente.telefono = request.form['telefono']
    cliente.email = request.form['email']
    cliente.direccion = request.form['direccion']

    pedido.forma_entrega = request.form['forma_entrega']
    pedido.estado = request.form['estado']

    for detalle in pedido.detalles:
        db.session.delete(detalle)

    productos = request.form.getlist('producto[]')
    sabores = request.form.getlist('sabor[]')
    cantidades = request.form.getlist('cantidad[]')
    observaciones = request.form.getlist('observaciones[]')

    for prod, sabor, cant, obs in zip(productos, sabores, cantidades, observaciones):
        producto = Producto.query.filter_by(nombre=prod, sabor=sabor).first()
        if producto:
            nuevo_detalle = DetallePedido(
                pedido_id=pedido.id,
                producto_id=producto.id,
                cantidad=int(cant),
                observaciones=obs.strip() or None
            )
            db.session.add(nuevo_detalle)

    db.session.commit()
    return redirect(url_for('detalle_pedido_cliente', pedido_id=pedido_id))


@app.route('/rastreo')
def rastreo():
    return render_template('rastreo.html')


@app.route('/ver_estado_pedido', methods=['POST'])
def ver_estado_pedido():

    try:
        numero = int(request.form['numero'])
        pedido = db.session.get(Pedido, numero)


        
        if pedido:
            estado = pedido.estado or 'registrado'
            mensaje = f"📦 El estado actual del pedido #{numero:04d} es: {estado.upper()}"
            clase_color = 'verde'
        else:
            mensaje = "❌ No se encontró el pedido. Verifica el número ingresado."
            clase_color = 'rojo'
            pedido = None

    except ValueError:
        mensaje = "⚠️ Número inválido. Intenta nuevamente."
        clase_color = 'rojo'
        pedido = None

    return render_template('rastreo.html', mensaje=mensaje, clase_color=clase_color, pedido=pedido)



@app.route('/cancelar_pedido/<int:pedido_id>', methods=['POST'])
def cancelar_pedido(pedido_id):

    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        return "Pedido no encontrado", 404
    
    estado_actual = pedido.estado.lower()

    mensajes_estado = {
        'registrado': "✅ El pedido ha sido cancelado exitosamente. Gracias por avisarnos.",
        'preparacion': "⚠️ No se puede cancelar el pedido porque ya está en preparación. Por favor, <a href='/contactanos'><strong>contacta a nuestro servicio al cliente</strong></a> si necesitas más ayuda.",
        'listo': "⚠️ Tu pedido ya está listo para ser entregado o recogido. En esta etapa no es posible cancelarlo. <a href='/contactanos'><strong>Contacta al servicio al cliente</strong></a> para mayor asistencia.",
        'en camino': "📦 El pedido ya está en camino y no puede ser cancelado. Puedes rechazarlo en la entrega  o <a href='/contactanos'><strong>escribirnos aquí</strong></a>.",
        'entregado': "🚚 El pedido ya fue entregado. Si tienes inconvenientes, por favor <a href='/contactanos'><strong>contacta a nuestro equipo de soporte</strong></a>.",
        'cancelado': "ℹ️ Este pedido ya fue cancelado anteriormente. Si fue un error, por favor <a href='/contactanos'><strong>crea uno nuevo o contáctanos</strong></a>.",
    }

    if estado_actual != "registrado":
        mensaje = mensajes_estado.get(estado_actual, "⚠️ No se puede cancelar el pedido debido a un estado desconocido. <a href='/contactanos'><strong>Contáctanos</strong></a> para revisar el caso.")
        return render_template("rastreo.html", mensaje=mensaje, clase_color="rojo", pedido=pedido, pedido_id=pedido_id)
    
    pedido.estado = "cancelado"
    try:
        db.session.commit()
        mensaje = mensajes_estado['registrado']
        return render_template("rastreo.html", mensaje=mensaje, clase_color="verde", pedido=pedido)
    except Exception as e:
        return f"Error al cancelar el pedido: {e}", 500
  
if __name__ == '__main__':
    # Configuración para Render
    port = int(os.environ.get('PORT', 5000))  
    app.run(debug=True, host='0.0.0.0', port=port)
    with app.app_context():
        db.create_all()
    app.run(debug=True)

    # Para desarrollo local, puedes usar:
    #app.run(debug=True, port=5000)  