from flask import Flask
from models import db, Pedido, DetallePedido
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Suponiendo que Luis (cliente_id=1) existe y productos con id 1 y 2 también
    pedido = Pedido(
        cliente_id=1,
        forma_entrega='Domicilio',
        estado='registrado',
        fecha_hora=datetime.now()
    )
    db.session.add(pedido)
    db.session.commit()

    detalles = [
        DetallePedido(pedido_id=pedido.id, producto_id=1, cantidad=2, observaciones='Sin sal'),
        DetallePedido(pedido_id=pedido.id, producto_id=2, cantidad=1, observaciones='Con limón')
    ]
    db.session.add_all(detalles)
    db.session.commit()

    print("✅ Pedido y detalles cargados.")
