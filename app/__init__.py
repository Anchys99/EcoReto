from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()  # Carga las variables del archivo .env

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'tu_clave_secreta'
    
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app