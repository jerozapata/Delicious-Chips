from flask import Flask
from models import db, Producto

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_datos_delicious.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

productos = [
    # Papas
    ("Papas", "Natural", "30g", 1300), ("Papas", "Natural", "50g", 1800), ("Papas", "Natural", "70g", 2500),
    ("Papas", "Limón", "30g", 1300), ("Papas", "Limón", "50g", 1800), ("Papas", "Limón", "70g", 2500),
    ("Papas", "Limón pimienta", "30g", 1300), ("Papas", "Limón pimienta", "50g", 1800), ("Papas", "Limón pimienta", "70g", 2500),
    ("Papas", "Mayonesa", "30g", 1300), ("Papas", "Mayonesa", "50g", 1800), ("Papas", "Mayonesa", "70g", 2500),
    ("Papas", "Pollo", "30g", 1300), ("Papas", "Pollo", "50g", 1800), ("Papas", "Pollo", "70g", 2500),
    ("Papas", "BBQ picante", "30g", 1300), ("Papas", "BBQ picante", "50g", 1800), ("Papas", "BBQ picante", "70g", 2500),
    
    # Plátano
    ("Plátano", "Verde natural", "50g", 1800), ("Plátano", "Verde natural", "70g", 2500),
    ("Plátano", "Verde limón", "50g", 1800), ("Plátano", "Verde limón", "70g", 2500),
    ("Plátano", "Maduro natural", "50g", 1800), ("Plátano", "Maduro natural", "70g", 2500),
    ("Plátano", "Maduro limón", "50g", 1800), ("Plátano", "Maduro limón", "70g", 2500),

    # Chicharrón
    ("Chicharrón", "Natural", "35g", 2200),
    ("Chicharrón", "Limón", "35g", 2200),

    # Extrudos
    ("Extrudos", "Aros limón", "50g", 1700),
    ("Extrudos", "Rosquillas limón", "50g", 1700),
    ("Extrudos", "Tocineta miel", "50g", 1700),
    ("Extrudos", "Chicharrin natural", "50g", 1700),
    ("Extrudos", "Chicharrin limón", "50g", 1700)
]

with app.app_context():
    for nombre, sabor, gramaje, precio_unitario in productos:
        prod = Producto(nombre=nombre, sabor=sabor, gramaje=gramaje, precio_unitario=precio_unitario)
        db.session.add(prod)
    db.session.commit()
    print("✅ Productos cargados.")
