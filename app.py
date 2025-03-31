import os
from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import config
from models import db, User
from flask_wtf.csrf import CSRFProtect
from waitress import serve

migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user and user.company:
        # Verifica se a empresa tem acesso
        if not user.company.check_access():
            return None
    return user

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Cria diretório de uploads se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Registra blueprints
    from routes.auth import auth  # Modifique estas importações
    from routes.main import main
    from routes.api import api
    from routes.admin import admin
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(admin)
    
    # Rota raiz para redirecionar para a página principal
    @app.route('/')
    def index():
        return redirect(url_for('main.index'))
    
    return app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    # Executa a aplicação usando Waitress
    print(f"Starting Waitress server on http://0.0.0.0:{os.getenv('PORT', 5000)}")
    serve(
        app,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )
