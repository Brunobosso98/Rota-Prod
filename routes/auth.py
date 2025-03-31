from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User, Company, Plan  # Import Plan model
from forms import LoginForm, AdminRegistrationForm, ProfileForm, UserCreateForm, UserAssignForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.company and not user.company.check_access():
                flash('Sua empresa não tem mais acesso ao sistema. Entre em contato com o suporte.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        flash('Email ou senha inválidos.', 'danger')
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        # Verifica se o email já existe
        if User.query.filter_by(email=form.email.data).first():
            flash('Email já cadastrado', 'danger')
            return render_template('auth/register.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Nome de usuário já em uso', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Verifica se o CNPJ já existe
        existing_company = Company.query.filter_by(cnpj=form.cnpj.data).first()
        
        if existing_company:
            # Verifica se já existe um administrador para este CNPJ
            existing_admin = User.query.filter_by(company_id=existing_company.id, role='admin').first()
            if existing_admin:
                flash('Já existe um administrador cadastrado para este CNPJ', 'danger')
                return render_template('auth/register.html', form=form)
            
            # CNPJ existe mas não tem admin, então podemos criar um novo admin para esta empresa
            admin = User(
                username=form.username.data,
                email=form.email.data,
                role='admin',
                company_id=existing_company.id
            )
            admin.set_password(form.password.data)
            
            db.session.add(admin)
            db.session.commit()
            
            flash('Administrador cadastrado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
        else:
            # Buscar o plano Trial
            trial_plan = Plan.query.filter_by(name='Trial').first()
            if not trial_plan:
                flash('Erro interno: Plano Trial não encontrado. Contate o suporte.', 'danger')
                return render_template('auth/register.html', form=form)

            # Criar uma nova empresa com o plano Trial
            company = Company(
                name=form.company_name.data,
                cnpj=form.cnpj.data,
                plan_id=trial_plan.id  # Definir o plano Trial
            )

            db.session.add(company)
            db.session.flush()  # Para obter o ID da empresa
            
            # Criar o usuário administrador
            admin = User(
                username=form.username.data,
                email=form.email.data,
                role='admin',
                company_id=company.id
            )
            admin.set_password(form.password.data)
            
            db.session.add(admin)
            db.session.commit()
            
            flash('Empresa e administrador cadastrados com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    # Preencher o CNPJ da empresa no formulário
    if current_user.company:
        form.company_cnpj.data = current_user.company.cnpj
    
    if form.validate_on_submit():
        # Verifica se o email já está em uso por outro usuário
        if form.email.data != current_user.email:
            if User.query.filter_by(email=form.email.data).first():
                flash('Email já está em uso por outro usuário', 'danger')
                return render_template('auth/profile.html', form=form)
        
        # Verifica se o username já está em uso por outro usuário
        if form.username.data != current_user.username:
            if User.query.filter_by(username=form.username.data).first():
                flash('Nome de usuário já está em uso', 'danger')
                return render_template('auth/profile.html', form=form)
        
        # Atualiza os dados do usuário
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        # Se uma nova senha foi fornecida, verifica a senha atual
        if form.new_password.data:
            if not current_user.check_password(form.current_password.data):
                flash('Senha atual incorreta', 'danger')
                return render_template('auth/profile.html', form=form)
            
            current_user.set_password(form.new_password.data)
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.profile'))
    else:
        # Preencher o formulário com os dados atuais
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('auth/profile.html', form=form)

@auth.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    # Verificar se o usuário atual é admin ou gerente
    if not (current_user.is_admin() or current_user.is_manager()):
        abort(403)  # Acesso negado
    
    form = UserCreateForm()
    
    # Se o usuário for um gerente, só pode criar vendedores
    if current_user.is_manager():
        form.role.choices = [('seller', 'Vendedor')]
    
    if form.validate_on_submit():
        # Verificar se o email já existe
        if User.query.filter_by(email=form.email.data).first():
            flash('Email já cadastrado', 'danger')
            return render_template('auth/create_user.html', form=form)
        
        # Verificar se o username já existe
        if User.query.filter_by(username=form.username.data, company_id=current_user.company_id).first():
            flash('Nome de usuário já em uso nesta empresa', 'danger')
            return render_template('auth/create_user.html', form=form)
        
        # Criar o novo usuário
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            company_id=current_user.company_id
        )
        new_user.set_password(form.password.data)
        
        db.session.add(new_user)
        
        # Se o criador for gerente e o novo usuário for vendedor, adicionar à lista de gerenciados
        if current_user.is_manager() and form.role.data == 'seller':
            current_user.managed_sellers.append(new_user)
        
        db.session.commit()
        
        flash(f'Usuário {new_user.username} criado com sucesso!', 'success')
        return redirect(url_for('main.manage_users'))
    
    return render_template('auth/create_user.html', form=form)

@auth.route('/users/assign/managers/<int:seller_id>', methods=['GET', 'POST'])
@login_required
def assign_managers_to_seller(seller_id):
    # Somente administradores podem atribuir gerentes a vendedores
    if not current_user.is_admin():
        abort(403)
    
    seller = User.query.get_or_404(seller_id)
    if seller.role != 'seller' or seller.company_id != current_user.company_id:
        abort(404)
    
    form = UserAssignForm()
    
    # Obter todos os gerentes da mesma empresa
    managers = User.query.filter_by(role='manager', company_id=current_user.company_id).all()
    form.users.choices = [(m.id, m.username) for m in managers]
    
    # Pre-selecionar gerentes já atribuídos
    current_managers = [m.id for m in seller.managers.all()]
    
    if form.validate_on_submit():
        # Atribuir o vendedor aos gerentes selecionados
        for manager in managers:
            # Se o gerente foi selecionado e o vendedor não está atribuído a ele
            if manager.id in form.users.data and seller.id not in [s.id for s in manager.managed_sellers.all()]:
                manager.managed_sellers.append(seller)
            # Se o gerente não foi selecionado mas o vendedor está atribuído a ele
            elif manager.id not in form.users.data and seller.id in [s.id for s in manager.managed_sellers.all()]:
                manager.managed_sellers.remove(seller)
        
        db.session.commit()
        flash(f'Gerentes atribuídos ao vendedor {seller.username} com sucesso!', 'success')
        return redirect(url_for('main.manage_users'))
    
    # Pré-selecionar gerentes atuais
    form.users.data = current_managers
    
    return render_template('auth/assign_users.html', form=form, title=f'Atribuir Gerentes ao Vendedor: {seller.username}', user=seller)

@auth.route('/users/assign/sellers/<int:manager_id>', methods=['GET', 'POST'])
@login_required
def assign_sellers_to_manager(manager_id):
    # Somente administradores podem atribuir vendedores a gerentes
    if not current_user.is_admin():
        abort(403)
    
    manager = User.query.get_or_404(manager_id)
    if manager.role != 'manager' or manager.company_id != current_user.company_id:
        abort(404)
    
    form = UserAssignForm()
    
    # Obter todos os vendedores da mesma empresa
    sellers = User.query.filter_by(role='seller', company_id=current_user.company_id).all()
    form.users.choices = [(s.id, s.username) for s in sellers]
    
    # Pre-selecionar vendedores já atribuídos
    current_sellers = [s.id for s in manager.managed_sellers.all()]
    
    if form.validate_on_submit():
        # Atribuir os vendedores selecionados ao gerente
        for seller in sellers:
            # Se o vendedor foi selecionado e não está atribuído ao gerente
            if seller.id in form.users.data and seller.id not in [s.id for s in manager.managed_sellers.all()]:
                manager.managed_sellers.append(seller)
            # Se o vendedor não foi selecionado mas está atribuído ao gerente
            elif seller.id not in form.users.data and seller.id in [s.id for s in manager.managed_sellers.all()]:
                manager.managed_sellers.remove(seller)
        
        db.session.commit()
        flash(f'Vendedores atribuídos ao gerente {manager.username} com sucesso!', 'success')
        return redirect(url_for('main.manage_users'))
    
    # Pré-selecionar vendedores atuais
    form.users.data = current_sellers
    
    return render_template('auth/assign_users.html', form=form, title=f'Atribuir Vendedores ao Gerente: {manager.username}', user=manager)

@auth.route('/unassign_manager/<int:seller_id>', methods=['POST'])
@login_required
def unassign_manager(seller_id):
    """Desvincula um gerente de um vendedor"""
    if not current_user.is_admin():
        flash('Você não tem permissão para realizar esta ação.', 'error')
        return redirect(url_for('main.index'))
    
    seller = User.query.get_or_404(seller_id)
    
    # Verificar se o vendedor pertence à mesma empresa do admin
    if seller.company_id != current_user.company_id:
        flash('Você não tem permissão para gerenciar este vendedor.', 'error')
        return redirect(url_for('main.index'))
    
    # Obter o ID do gerente a ser desvinculado
    manager_id = request.form.get('manager_id')
    if not manager_id:
        flash('Gerente não especificado.', 'error')
        return redirect(url_for('auth.assign_managers_to_seller', seller_id=seller_id))
    
    manager = User.query.get_or_404(manager_id)
    
    # Verificar se o gerente pertence à mesma empresa
    if manager.company_id != current_user.company_id:
        flash('Gerente não pertence à sua empresa.', 'error')
        return redirect(url_for('auth.assign_managers_to_seller', seller_id=seller_id))
    
    # Remover o relacionamento
    if manager in seller.managers:
        seller.managers.remove(manager)
        db.session.commit()
        flash(f'Gerente {manager.display_name} desvinculado do vendedor {seller.display_name}.', 'success')
    else:
        flash('Este gerente não está vinculado ao vendedor.', 'error')
    
    return redirect(url_for('auth.assign_managers_to_seller', seller_id=seller_id))

@auth.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Exclui uma conta de usuário (gerente ou vendedor)"""
    user_to_delete = User.query.get_or_404(user_id)
    
    # Verificar permissões
    if not current_user.is_admin():
        if current_user.is_manager():
            # Gerentes só podem excluir vendedores que gerenciam
            if user_to_delete.role != 'seller' or user_to_delete not in current_user.managed_sellers:
                flash('Você não tem permissão para excluir este usuário.', 'error')
                return redirect(url_for('main.index'))
        else:
            flash('Você não tem permissão para excluir usuários.', 'error')
            return redirect(url_for('main.index'))
    
    # Verificar se o usuário pertence à mesma empresa
    if user_to_delete.company_id != current_user.company_id:
        flash('Você não tem permissão para excluir este usuário.', 'error')
        return redirect(url_for('main.index'))
    
    # Não permitir excluir o próprio usuário
    if user_to_delete.id == current_user.id:
        flash('Você não pode excluir sua própria conta.', 'error')
        return redirect(url_for('main.index'))
    
    # Não permitir excluir administradores
    if user_to_delete.role == 'admin':
        flash('Não é possível excluir contas de administradores.', 'error')
        return redirect(url_for('main.index'))
    
    # Excluir o usuário
    db.session.delete(user_to_delete)
    db.session.commit()
    
    flash(f'Conta de {user_to_delete.display_name} excluída com sucesso.', 'success')
    return redirect(url_for('main.index'))

@auth.route('/unassign_seller/<int:manager_id>', methods=['POST'])
@login_required
def unassign_seller(manager_id):
    """Desvincula um vendedor de um gerente"""
    if not current_user.is_admin():
        flash('Você não tem permissão para realizar esta ação.', 'error')
        return redirect(url_for('main.index'))
    
    manager = User.query.get_or_404(manager_id)
    
    # Verificar se o gerente pertence à mesma empresa do admin
    if manager.company_id != current_user.company_id:
        flash('Você não tem permissão para gerenciar este gerente.', 'error')
        return redirect(url_for('main.index'))
    
    # Obter o ID do vendedor a ser desvinculado
    seller_id = request.form.get('seller_id')
    if not seller_id:
        flash('Vendedor não especificado.', 'error')
        return redirect(url_for('auth.assign_sellers_to_manager', manager_id=manager_id))
    
    seller = User.query.get_or_404(seller_id)
    
    # Verificar se o vendedor pertence à mesma empresa
    if seller.company_id != current_user.company_id:
        flash('Vendedor não pertence à sua empresa.', 'error')
        return redirect(url_for('auth.assign_sellers_to_manager', manager_id=manager_id))
    
    # Remover o relacionamento
    if seller in manager.managed_sellers:
        manager.managed_sellers.remove(seller)
        db.session.commit()
        flash(f'Vendedor {seller.display_name} desvinculado do gerente {manager.display_name}.', 'success')
    else:
        flash('Este vendedor não está vinculado ao gerente.', 'error')
    
    return redirect(url_for('auth.assign_sellers_to_manager', manager_id=manager_id))
