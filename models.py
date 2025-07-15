from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    documento = db.Column(db.String, unique=True, nullable=False)
    telefono = db.Column(db.String)
    direccion = db.Column(db.String)
    email = db.Column(db.String, unique=True)

    pedidos = db.relationship('Pedido', back_populates='cliente')  # ✅ corregido

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    sabor = db.Column(db.String, nullable=False)
    gramaje = db.Column(db.String, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

    detalles = db.relationship('DetallePedido', backref='producto', lazy=True)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    forma_entrega = db.Column(db.String, nullable=False)
    estado = db.Column(db.String, default='registrado')
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship('Cliente', back_populates='pedidos')  # ✅ corregido
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True)

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    observaciones = db.Column(db.String)

    

class Contacto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    documento = db.Column(db.String(20))
    correo = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
    mensaje = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
