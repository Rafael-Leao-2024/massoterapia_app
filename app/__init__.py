# app/__init__.py
from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from werkzeug.middleware.proxy_fix import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    from app.models.user import User
    from app.models.agendamento import Agendamento
    from app.models.depoimento import Depoimento

    # Importar relacionamentos depois
    from app.models.relacao import User, Agendamento, Depoimento
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.cliente.routes import cliente_bp
    from app.main.routes import main_bp
    from app.depoimentos.routes import depoimentos_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cliente_bp, url_prefix='/cliente')
    app.register_blueprint(main_bp)
    app.register_blueprint(depoimentos_bp, url_prefix='/depoimentos')
    
    return app