from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
import os
from dotenv import load_dotenv

# Inicializar extensões
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página'

def create_app():
    # Carregar variáveis de ambiente
    load_dotenv()
    
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendario.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensões com o app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Importar e registrar blueprints
    with app.app_context():
        from backend.routes.routes import main
        app.register_blueprint(main)
    
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    return app 