from app import create_app
from models import db, Plan, Company, User
import os

def setup_database():
    """Configura o banco de dados inicial"""
    app = create_app('production')
    
    # Configure database connection
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://bbmartins:QczR6x4jX8kYxXhTfqmdjyxjmXDQypyG@dpg-cvl6t2i4d50c73e2osu0-a.virginia-postgres.render.com/siterta')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        print("Criando tabelas...")
        db.create_all()
        
        # Criar planos iniciais
        if not Plan.query.first():
            print("Criando planos iniciais...")
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
            
            db.session.add(free_plan)
            db.session.add(pro_plan)
            db.session.commit()
            
        # Criar empresa e usuário admin inicial
        if not User.query.filter_by(is_super=True).first():
            print("Criando usuário admin...")
            company = Company(
                name="Conttrolare",
                cnpj="54687654345675",
                plan_id=1  # ID do plano Trial
            )
            db.session.add(company)
            db.session.flush()
            
            admin = User(
                username="Admin",
                email="admin@conttrolare.com",
                company_id=company.id,
                role='admin',
                is_super=True
            )
            admin.set_password("admin123")  # Mude esta senha!
            
            db.session.add(admin)
            db.session.commit()
            
        print("Configuração do banco concluída!")

if __name__ == '__main__':
    setup_database()
from app import create_app
from models import db, Plan, Company, User
import os

def setup_database():
    """Configura o banco de dados inicial"""
    app = create_app('production')
    
    # Configure database connection
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://bbmartins:QczR6x4jX8kYxXhTfqmdjyxjmXDQypyG@dpg-cvl6t2i4d50c73e2osu0-a.virginia-postgres.render.com/siterta')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        print("Criando tabelas...")
        db.create_all()
        
        # Criar planos iniciais
        if not Plan.query.first():
            print("Criando planos iniciais...")
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
            
            db.session.add(free_plan)
            db.session.add(pro_plan)
            db.session.commit()
            
        # Criar empresa e usuário admin inicial
        if not User.query.filter_by(is_super=True).first():
            print("Criando usuário admin...")
            company = Company(
                name="Conttrolare",
                cnpj="54687654345675",
                plan_id=1  # ID do plano Trial
            )
            db.session.add(company)
            db.session.flush()
            
            admin = User(
                username="Admin",
                email="admin@conttrolare.com",
                company_id=company.id,
                role='admin',
                is_super=True
            )
            admin.set_password("admin123")  # Mude esta senha!
            
            db.session.add(admin)
            db.session.commit()
            
        print("Configuração do banco concluída!")

if __name__ == '__main__':
    setup_database()
