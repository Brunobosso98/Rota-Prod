from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from models import Company, Plan
from forms import ChangePlanForm
from datetime import timezone

admin = Blueprint('admin', __name__)

@admin.route('/admin/companies')
@login_required
def list_companies():
    """Lista todas as empresas (apenas super admin)"""
    if not current_user.is_super_admin():
        abort(403)
    
    companies = Company.query.all()
    return render_template('admin/companies.html', companies=companies)

@admin.route('/admin/company/<int:company_id>/change-plan', methods=['GET', 'POST'])
@login_required
def change_company_plan(company_id):
    """Muda o plano de uma empresa"""
    if not current_user.is_super_admin():
        abort(403)
    
    company = Company.query.get_or_404(company_id)
    form = ChangePlanForm()
    
    # Preencher as escolhas do plano
    form.plan.choices = [(p.id, p.name) for p in Plan.query.all()]
    
    if form.validate_on_submit():
        company.plan_id = form.plan.data
        company.is_active = True
        from datetime import datetime
        company.plan_started_at = datetime.now(timezone.utc)
        
        db.session.commit()
        flash(f'Plano da empresa {company.name} atualizado com sucesso!', 'success')
        return redirect(url_for('admin.list_companies'))
    
    # Pré-selecionar o plano atual
    form.plan.data = company.plan_id
    
    return render_template('admin/change_plan.html', form=form, company=company)