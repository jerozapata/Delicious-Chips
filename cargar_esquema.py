from flask import Flask
from models import db

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_datos_delicious.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Base de datos creada exitosamente en /instance/base_datos_delicious.db")
