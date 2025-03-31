from flask import Flask
from models import db
from flask_migrate import Migrate, upgrade
import os

def create_app():
    app = Flask(__name__)
    
    # Configuração do banco de dados PostgreSQL
    DB_USER = '10.253.248.141'
    DB_PASSWORD = 'rtapw'
    DB_HOST = 'siterta'
    DB_PORT = '5432'
    DB_NAME = 'rta'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensões
    db.init_app(app)
    Migrate(app, db)
    
    return app

def setup_database():
    """Configura o banco de dados e aplica as migrações"""
    app = create_app()
    
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        print("Tabelas criadas com sucesso!")
        
        print("Configuração do banco de dados concluída!")

if __name__ == '__main__':
    setup_database() 