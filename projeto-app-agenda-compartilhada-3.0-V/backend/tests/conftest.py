import pytest
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from backend import db
from backend.models.models import User, Family, Event, Task

@pytest.fixture
def app():
    app = Flask(__name__)
    
    # Configurar caminhos dos templates e arquivos estáticos
    app.template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/templates'))
    app.static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/static'))
    
    # Configurações do app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'chave_de_teste'
    app.config['WTF_CSRF_ENABLED'] = False  # Desabilita CSRF para testes
    app.config['LOGIN_DISABLED'] = False
    app.config['SERVER_NAME'] = 'localhost'  # Necessário para url_for funcionar em testes
    
    # Configurar Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    # Configurar CSRF
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    db.init_app(app)

    with app.app_context():
        # Registrar blueprint
        from backend.routes.routes import main
        app.register_blueprint(main)
        
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session
