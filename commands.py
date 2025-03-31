import click
from flask.cli import with_appcontext
from app import db
from models import Company, Plan
from datetime import timezone

def register_commands(app):
    @app.cli.command('change-plan')
    @click.argument('cnpj')
    @click.argument('plan_name')
    @with_appcontext
    def change_company_plan(cnpj, plan_name):
        """
        Muda o plano de uma empresa.
        Uso: flask change-plan CNPJ PLAN_NAME
        Exemplo: flask change-plan 12345678901234 Enterprise
        """
        try:
            # Encontrar a empresa
            company = Company.query.filter_by(cnpj=cnpj).first()
            if not company:
                click.echo(f'Empresa com CNPJ {cnpj} não encontrada.')
                return
            
            # Encontrar o plano
            plan = Plan.query.filter_by(name=plan_name).first()
            if not plan:
                click.echo(f'Plano {plan_name} não encontrado.')
                return
            
            # Atualizar o plano
            company.plan_id = plan.id
            company.is_active = True
            from datetime import datetime
            company.plan_started_at = datetime.now(timezone.utc)
            
            db.session.commit()
            click.echo(f'Plano da empresa {company.name} atualizado para {plan.name} com sucesso!')
            
        except Exception as e:
            click.echo(f'Erro ao atualizar plano: {str(e)}')