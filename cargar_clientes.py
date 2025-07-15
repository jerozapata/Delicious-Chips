from flask import Flask
from models import db, Cliente

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_datos_delicious.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

clientes = [
    ("Luis Rodríguez", "123456789", "3124567890", "Cra 45 #12-34", "luis@example.com"),
    ("Ana Gómez", "987654321", "3101234567", "Calle 10 #20-30", "ana@example.com")
]

with app.app_context():
    for nombre, doc, tel, dir, email in clientes:
        c = Cliente(nombre=nombre, documento=doc, telefono=tel, direccion=dir, email=email)
        db.session.add(c)
    db.session.commit()
    print("✅ Clientes cargados.")

