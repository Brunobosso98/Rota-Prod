#!/usr/bin/env python
"""
Script para recriar o banco de dados do zero.
Este script irá apagar todas as tabelas existentes e criar novas tabelas com o esquema atualizado.
"""

import os
from app import create_app  # Importa do app.py
from models import db, User, Route, RoutePoint, Location, RouteLocation, Company, Plan

def recreate_database():
    """Recria o banco de dados apagando todas as tabelas e criando-as novamente"""
    try:
        app = create_app(os.getenv('FLASK_CONFIG') or 'default')
        
        with app.app_context():
            print("Iniciando recriação do banco de dados...")
            
            # Confirmar com o usuário
            if input("ATENÇÃO: Todos os dados serão perdidos! Digite 'SIM' para confirmar: ") != "SIM":
                print("Operação cancelada.")
                return False
            
            print("Apagando todas as tabelas...")
            db.drop_all()
            print("Todas as tabelas foram apagadas com sucesso.")
            
            print("Criando novas tabelas com o esquema atualizado...")
            db.create_all()
            print("Novas tabelas criadas com sucesso.")
            
            print("Processo concluído! O banco de dados foi recriado com sucesso.")
            print("Agora você precisa criar um usuário administrador para começar a usar o sistema.")
            
            return True
    except Exception as e:
        print(f"Erro ao recriar banco de dados: {str(e)}")
        return False

def create_initial_plans():
    """Cria os planos iniciais do sistema"""
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    with app.app_context():
        # Plano gratuito de 7 dias
        free_plan = Plan(
            name='Trial',
            description='Plano gratuito de 7 dias para teste do sistema',
            is_free=True,
            duration_days=7
        )

        pro_plan = Plan(
            name='Pro',
            description='Plano gratuito de 30 dias para teste do sistema',
            is_free=True,
            duration_days=30
        )
        
        # Plano ilimitado
        unlimited_plan = Plan(
            name='Enterprise',
            description='Plano empresarial com acesso ilimitado',
            is_free=False,
            duration_days=None  # None significa ilimitado
        )
        
        db.session.add(free_plan)
        db.session.add(pro_plan)
        db.session.add(unlimited_plan)
        db.session.commit()
        
        print("Planos iniciais criados com sucesso!")
        
def create_admin_user():
    """Cria um usuário administrador inicial"""
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    with app.app_context():
        print("\n=== Criação de Usuário Administrador ===")
        print("Você deseja criar um usuário administrador agora?")
        
        if input("Digite 'SIM' para criar um admin ou qualquer outra coisa para pular: ") != "SIM":
            print("Criação de admin pulada.")
            return False
        
        company_name = "Conttrolare"
        company_cnpj = 54687654345675
        
        # Pegar o plano gratuito
        free_plan = Plan.query.filter_by(is_free=True).first()
        
        # Criar empresa com o plano gratuito
        company = Company(
            name=company_name,
            cnpj=company_cnpj,
            plan_id=free_plan.id
        )
        db.session.add(company)
        db.session.commit()
        
        # Dados do usuário
        username = "Ricardo Samogin"
        email = "ricardo@conttrolare.com"
        password = "123123"
        
        # Criar usuário admin como super admin
        admin = User(
            username=username,
            email=email,
            company_id=company.id,
            role='admin',
            is_super=True  # Adicionada esta linha
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Usuário super administrador '{username}' criado com sucesso!")
        print(f"Agora você pode fazer login com: {username} / {password}")
        
        return True

if __name__ == '__main__':
    print("===== RECRIAÇÃO DO BANCO DE DADOS =====")
    print("Este script irá apagar TODAS as tabelas e dados existentes e criar um banco de dados vazio.")
    
    if recreate_database():
        create_initial_plans()
        create_admin_user()
    
    print("\nProcesso concluído.") 
