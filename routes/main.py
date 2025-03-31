from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app, abort
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from models import User, Route, RoutePoint, Location, RouteLocation, db
from models import db, Route, RoutePoint, Location, User, Company, RouteLocation
from forms import RouteForm, LocationForm, CompleteRouteForm, CloneRouteForm, EditRouteForm
from app import mail
import pandas as pd
import os
from datetime import datetime, timezone, timedelta
import time
import folium
from werkzeug.utils import secure_filename
import uuid
import math
from utils.geo import haversine
import polyline
from threading import Thread
from sqlalchemy import or_, func

main = Blueprint('main', __name__)

class AppSettings:
    """Classe para gerenciar configurações da aplicação"""
    def __init__(self):
        self.distance_threshold = 100  # Valor padrão: 100 metros

# Instância global das configurações
app_settings = AppSettings()

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Estatísticas e informações pertinentes à função do usuário
    company = Company.query.get(current_user.company_id)
    
    if current_user.is_admin():
        # Administrador vê todas as rotas e usuários da empresa
        routes = Route.query.filter_by(company_id=current_user.company_id).order_by(Route.created_at.desc()).all()
        locations = Location.query.filter_by(company_id=current_user.company_id).all()
        users = User.query.filter_by(company_id=current_user.company_id).all()
        
        total_managers = User.query.filter_by(company_id=current_user.company_id, role='manager').count()
        total_sellers = User.query.filter_by(company_id=current_user.company_id, role='seller').count()
        
    elif current_user.is_manager():
        # Gerente vê rotas que criou e de vendedores que gerencia
        managed_sellers_ids = [seller.id for seller in current_user.managed_sellers]
        routes = Route.query.filter(
            (Route.creator_id == current_user.id) | 
            (Route.creator_id.in_(managed_sellers_ids))
        ).order_by(Route.created_at.desc()).all()
        
        locations = Location.query.filter_by(creator_id=current_user.id).all()
        users = User.query.filter(
            (User.id.in_(managed_sellers_ids)) | 
            (User.id == current_user.id)
        ).all()
        
        total_managers = 1  # O próprio gerente
        total_sellers = len(managed_sellers_ids)
        
    else:  # Vendedor
        # Vendedor vê apenas suas rotas atribuídas
        routes = current_user.assigned_routes.all()
        locations = Location.query.filter_by(creator_id=current_user.id).all()
        users = [current_user]
        
        total_managers = 0
        total_sellers = 1  # O próprio vendedor
    
    # Estatísticas
    total_routes = len(routes)
    total_locations = len(locations)
    
    # Conta pontos visitados
    visited_points = 0
    for route in routes:
        visited_points += sum(1 for p in route.points if p.is_visited)
    
    # Rotas recentes (5 mais recentes)
    recent_routes = routes[:5] if len(routes) > 5 else routes
    
    # Rotas concluídas e não concluídas
    completed_routes = [r for r in routes if r.is_completed]
    active_routes = [r for r in routes if not r.is_completed]
    
    return render_template('main/dashboard.html',
                          company=company,
                          total_routes=total_routes,
                          total_locations=total_locations,
                          visited_points=visited_points,
                          recent_routes=recent_routes,
                          total_managers=total_managers,
                          total_sellers=total_sellers,
                          completed_routes=len(completed_routes),
                          active_routes=len(active_routes))

@main.route('/manage/users')
@login_required
def manage_users():
    # Apenas administradores e gerentes podem gerenciar usuários
    if current_user.is_seller():
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if current_user.is_admin():
        # Administrador vê todos os usuários da empresa
        managers = User.query.filter_by(company_id=current_user.company_id, role='manager').all()
        sellers = User.query.filter_by(company_id=current_user.company_id, role='seller').all()
    else:  # Gerente
        # Gerente vê apenas vendedores que gerencia
        managers = [current_user]
        sellers = current_user.managed_sellers.all()
    
    return render_template('main/manage_users.html', managers=managers, sellers=sellers)

@main.route('/locations')
@login_required
def locations():
    city_filter = request.args.get('city', '')
    state_filter = request.args.get('state', '')
    
    # Base query
    if current_user.is_admin():
        # Administrador vê todos os locais da empresa
        query = Location.query.filter_by(company_id=current_user.company_id)
    elif current_user.is_manager():
        # Gerente vê locais da empresa
        query = Location.query.filter_by(company_id=current_user.company_id)
    else:  # Vendedor
        # Vendedor vê locais que criou
        query = Location.query.filter_by(creator_id=current_user.id)
    
    # Aplicar filtros se fornecidos
    if city_filter:
        query = query.filter(Location.city.ilike(f'%{city_filter}%'))
    if state_filter:
        query = query.filter_by(state=state_filter)
    
    # Obter cidades e estados distintos para os filtros
    all_cities = db.session.query(Location.city).filter_by(company_id=current_user.company_id).distinct().all()
    all_states = db.session.query(Location.state).filter_by(company_id=current_user.company_id).distinct().all()
    
    # Executar a consulta
    locations = query.order_by(Location.state, Location.city, Location.name).all()
    
    return render_template(
        'main/locations.html', 
        locations=locations, 
        cities=[city[0] for city in all_cities], 
        states=[state[0] for state in all_states],
        city_filter=city_filter,
        state_filter=state_filter
    )

@main.route('/locations/add', methods=['GET', 'POST'])
@login_required
def add_location():
    form = LocationForm()
    
    if form.validate_on_submit():
        location = Location(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            telephone=form.telephone.data,
            creator_id=current_user.id,
            company_id=current_user.company_id
        )
        # Verificar se já existe um local com a mesma latitude e longitude na mesma empresa
        existing_location = Location.query.filter_by(
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            company_id=current_user.company_id
        ).first()
        
        if existing_location:
            flash('Já existe um local com a mesma latitude e longitude nesta empresa.', 'danger')
            return render_template('main/add_location.html', form=form)
        
        db.session.add(location)
        db.session.commit()
        
        flash(f'Local "{location.name}" adicionado com sucesso!', 'success')
        return redirect(url_for('main.locations'))
    
    return render_template('main/add_location.html', form=form)

def format_phone_number(phone):
    if not phone or pd.isna(phone):
        return None
        
    # Converte para string e remove caracteres não numéricos
    phone = str(phone).strip()
    numbers = ''.join(filter(str.isdigit, phone))
    
    if not numbers:
        return None
        
    # Formata o número baseado no tamanho
    if len(numbers) == 8:  # Fixo sem DDD
        return f"{numbers[:4]}-{numbers[4:]}"
    elif len(numbers) == 9:  # Celular sem DDD
        return f"{numbers[:5]}-{numbers[5:]}"
    elif len(numbers) == 10:  # Fixo com DDD
        return f"({numbers[:2]}) {numbers[2:6]}-{numbers[6:]}"
    elif len(numbers) == 11:  # Celular com DDD
        return f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}"
    else:
        return numbers  # Retorna os números sem formatação se não se encaixar nos padrões

@main.route('/locations/import', methods=['POST'])
@login_required
def import_locations():
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('main.locations'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('main.locations'))
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        flash('Arquivo inválido. Use apenas arquivos Excel (.xlsx, .xls)', 'danger')
        return redirect(url_for('main.locations'))
    
    try:
        # Salva o arquivo temporariamente
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Lê o arquivo Excel
        df = pd.read_excel(filepath)
        
        # Verifica se o arquivo tem as colunas necessárias
        required_columns = ['nome', 'cidade', 'estado', 'latitude', 'longitude']
        if not all(col.lower() in map(str.lower, df.columns) for col in required_columns):
            flash('O arquivo Excel não contém todas as colunas necessárias (nome, cidade, estado, latitude, longitude)', 'danger')
            return redirect(url_for('main.locations'))
        
        # Normaliza os nomes das colunas
        df.columns = df.columns.str.lower()
        
        # Remove linhas com valores nulos
        df = df.dropna(subset=['latitude', 'longitude', 'nome', 'cidade', 'estado'])
        
        # Converte coordenadas para float e valida
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        # Remove linhas com coordenadas inválidas
        df = df[
            (df['latitude'].between(-90, 90)) & 
            (df['longitude'].between(-180, 180))
        ]
        
        if df.empty:
            flash('Nenhuma coordenada válida encontrada no arquivo', 'danger')
            return redirect(url_for('main.locations'))
        
        # Adiciona os locais ao banco de dados
        count = 0
        for _, row in df.iterrows():
            telephone = format_phone_number(row.get('telefone')) if 'telefone' in df.columns else None
            street = row.get('rua') if 'rua' in df.columns else None # Get street if column exists
            
            # Handle 'numero' column, checking for 'SN' or 'S/N'
            number_raw = row.get('numero')
            number = None
            if 'numero' in df.columns and pd.notna(number_raw):
                number_str = str(number_raw).strip().lower()
                if number_str not in ['sn', 's/n']:
                    number = str(number_raw) # Keep original string if not SN or S/N

            # Verificar se já existe um local com a mesma latitude e longitude na mesma empresa
            existing_location = Location.query.filter_by(
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                company_id=current_user.company_id
            ).first()

            if existing_location:
                print(f"Local duplicado encontrado: {row['nome']}, {row['cidade']}, {row['estado']} (latitude={row['latitude']}, longitude={row['longitude']}). Ignorando.")
                continue  # Ignora este local e vai para o próximo

            location = Location(
                name=row['nome'],
                city=row['cidade'],
                state=row['estado'],
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                street=street,  # Add street
                number=number,  # Add number
                telephone=telephone,
                creator_id=current_user.id,
                company_id=current_user.company_id
            )
            db.session.add(location)
            count += 1

        db.session.commit()
        flash(f'{count} locais importados com sucesso!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao importar locais: {str(e)}', 'danger')
    finally:
        # Remove o arquivo temporário
        if os.path.exists(filepath):
            os.remove(filepath)
            
    return redirect(url_for('main.locations'))

@main.route('/locations/<int:location_id>/delete', methods=['DELETE'])
@login_required
def delete_location(location_id):
    # Get location and check permissions based on user role
    location = Location.query.get_or_404(location_id)
    
    if current_user.is_admin():
        if location.company_id != current_user.company_id:
            abort(403)
    elif current_user.is_manager():
        if location.company_id != current_user.company_id:
            abort(403)
    else:  # Seller
        if location.creator_id != current_user.id:
            abort(403)
    
    try:
        db.session.delete(location)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main.route('/locations/<int:location_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    
    # Verifica se o usuário tem permissão para editar este local
    if current_user.company_id != location.company_id:
        flash('Você não tem permissão para editar este local.', 'danger')
        return redirect(url_for('main.locations'))
    
    form = LocationForm(obj=location)
    
    if form.validate_on_submit():
        form.populate_obj(location)
        db.session.commit()
        flash(f'Local "{location.name}" atualizado com sucesso!', 'success')
        return redirect(url_for('main.locations'))
    
    return render_template('main/edit_location.html', form=form, location=location)

@main.route('/routes')
@login_required
def routes():    
    # Filtrar apenas rotas não completadas (is_completed = False) e que não são templates (is_template = False)
    if current_user.is_admin():
        routes = Route.query.filter_by(
            company_id=current_user.company_id,
            is_completed=False,
            is_template=False  # Adicionar este filtro
        ).order_by(Route.created_at.desc()).all()
    elif current_user.is_manager():
        managed_sellers_ids = [seller.id for seller in current_user.managed_sellers]
        routes = Route.query.filter(
            Route.company_id == current_user.company_id,
            Route.is_completed == False,
            Route.is_template == False,  # Adicionar este filtro
            or_(
                Route.creator_id == current_user.id,
                Route.creator_id.in_(managed_sellers_ids)
            )
        ).order_by(Route.created_at.desc()).all()
    else:  # vendedor
        routes = Route.query.filter(
            Route.company_id == current_user.company_id,
            Route.is_completed == False,
            Route.is_template == False,  # Adicionar este filtro
            or_(
                Route.creator_id == current_user.id,
                Route.id.in_([r.id for r in current_user.assigned_routes])
            )
        ).order_by(Route.created_at.desc()).all()

    # Agrupar rotas por criador
    routes_by_creator = {}
    for route in routes:
        creator = User.query.get(route.creator_id)
        creator_name = creator.username if creator else "Usuário Desconhecido"
        
        if creator_name not in routes_by_creator:
            routes_by_creator[creator_name] = []
        routes_by_creator[creator_name].append(route)
    
    return render_template('main/routes.html', routes_by_creator=routes_by_creator)

@main.route('/routes/completed')
@login_required
def completed_routes():
    if current_user.is_admin():
        # Administrador vê todas as rotas concluídas da empresa
        routes = Route.query.filter_by(company_id=current_user.company_id, is_completed=True).all()
    elif current_user.is_manager():
        # Gerente vê rotas concluídas que criou e de vendedores que gerencia
        managed_sellers_ids = [seller.id for seller in current_user.managed_sellers]
        routes = Route.query.filter(
            (Route.creator_id == current_user.id) | 
            (Route.creator_id.in_(managed_sellers_ids)),
            Route.is_completed == True
        ).all()
    else:  # Vendedor
        # Vendedor vê apenas suas rotas concluídas
        routes = current_user.assigned_routes.filter_by(is_completed=True).all()
    
    # Agrupar rotas por criador para melhor visualização
    routes_by_creator = {}
    for route in routes:
        creator = User.query.get(route.creator_id)
        if creator.username not in routes_by_creator:
            routes_by_creator[creator.username] = []
        routes_by_creator[creator.username].append(route)
    
    return render_template('main/completed_routes.html', routes_by_creator=routes_by_creator)

@main.route('/routes/create', methods=['GET', 'POST'])
@login_required
def create_route():
    if not current_user.can_create_route():
        abort(403)
    
    form = RouteForm()
    
    # Preencher o formulário com os dados necessários
    if current_user.is_admin():
        # Administradores podem ver todos os vendedores e gerentes
        form.sellers.choices = [(s.id, s.username) for s in User.query.filter_by(role='seller', company_id=current_user.company_id).all()]
        form.managers.choices = [(m.id, m.username) for m in User.query.filter_by(role='manager', company_id=current_user.company_id).all()]
    else:
        # Gerentes só podem ver seus próprios vendedores
        form.sellers.choices = [(s.id, s.username) for s in current_user.managed_sellers.all()]
        form.managers.choices = [(m.id, m.username) for m in User.query.filter_by(role='manager', company_id=current_user.company_id).all()]
    
    # Preencher as opções de localização
    locations = Location.query.filter_by(company_id=current_user.company_id).all()
    form.locations.choices = [(l.id, f"{l.name} - {l.city} - {l.state}") for l in locations]
    
    # Preencher estados para filtro
    states = sorted(list(set([l.state for l in locations])))
    form.state_filter.choices = [("", "Todos")] + [(state, state) for state in states]
    
    # Preencher cidades para filtro
    cities = sorted(list(set([l.city for l in locations])))
    form.city_filter.choices = [("", "Todas")] + [(city, city) for city in cities]
    
    # Ignorar validação para campos de filtro que são apenas para UI
    if request.method == 'POST':
        form.state_filter.data = ''
        form.city_filter.data = ''
    
    if form.validate_on_submit():
        try:
            # Adicionar logs para debug
            print(f"Criando rota com os seguintes dados:")
            print(f"Nome: {form.name.data}")
            print(f"Company ID: {current_user.company_id}")
            print(f"Creator ID: {current_user.id}")
            print("Formulário validado com sucesso!")
            
            # Verificar se há locais selecionados
            if not form.locations.data:
                print("Erro: Nenhum local selecionado!")
                flash('Por favor, selecione pelo menos um local para a rota.', 'danger')
                return render_template('main/create_route.html', form=form, title='Criar Nova Rota')
            
            print(f"Locais selecionados: {form.locations.data}")
                
            # Verificar se há vendedores selecionados (apenas para admin/gerente)
            if not form.sellers.data and (current_user.is_admin() or current_user.is_manager()):
                print("Erro: Nenhum vendedor selecionado!")
                flash('Por favor, selecione pelo menos um vendedor para a rota.', 'danger')
                return render_template('main/create_route.html', form=form, title='Criar Nova Rota')
            
            print(f"Vendedores selecionados: {form.sellers.data}")
                
            # Identificar o ponto de partida
            start_location_id = None
            print(f"Valor recebido para start_location: {request.form.get('start_location')}")
            if request.form.get('start_location'):
                try:
                    start_location_id = int(request.form.get('start_location'))
                    print(f"Ponto de partida selecionado: {start_location_id}")
                    start_location = Location.query.get(start_location_id)
                    if not start_location or start_location.company_id != current_user.company_id:
                        start_location_id = None
                except ValueError:
                    start_location_id = None

            # Se não foi selecionado um ponto de partida, usar o primeiro local da lista
            if not start_location_id and form.locations.data:
                start_location_id = form.locations.data[0]
                print(f"Usando primeiro local como ponto de partida: {start_location_id}")

            print("Criando a rota...")
            # Criar a nova rota
            route = Route(
                name=form.name.data,
                description=form.description.data,
                company_id=current_user.company_id,
                creator_id=current_user.id,
                created_at=datetime.now(timezone.utc)  # Adicionando esta linha
            )

            db.session.add(route)
            db.session.flush()  # Para obter o ID da rota
            print(f"Rota criada com ID: {route.id}")

            # Adicionar localizações e pontos da rota
            order_counter = 1

            # Primeiro, adicionar o ponto de partida se ele não estiver na lista de locations
            if start_location_id and int(start_location_id) not in [int(x) for x in form.locations.data]:
                start_location = Location.query.get(start_location_id)
                if start_location:
                    print(f"Adicionando ponto de partida {start_location.name} (ID: {start_location.id}) com ordem 0")
                    route_location = RouteLocation(
                        route_id=route.id,
                        location_id=start_location.id,
                        order=0,
                        distance_threshold=app_settings.distance_threshold
                    )
                    db.session.add(route_location)
                    
                    # Criar RoutePoint para o ponto de partida
                    route_point = RoutePoint(
                        latitude=start_location.latitude,
                        longitude=start_location.longitude,
                        name=start_location.name,
                        city=start_location.city,
                        state=start_location.state,
                        order=0,
                        route_id=route.id,
                        location_id=start_location.id
                    )
                    db.session.add(route_point)

            # Adicionar locais e pontos da rota
            for location_id in form.locations.data:
                # Convertemos para int para garantir comparação correta
                location_id = int(location_id)
                location = Location.query.get(location_id)
                if location:
                    # Definir ordem: 0 para o ponto de partida, incrementar para outros
                    order = 0 if location_id == int(start_location_id) else order_counter
                    
                    # Se for ponto que não é de partida, incrementar o contador
                    if location_id != int(start_location_id):
                        order_counter += 1
                    
                    print(f"Adicionando local {location.name} (ID: {location.id}) com ordem {order}")
                    
                    # Criar RouteLocation para associar Location com Route
                    route_location = RouteLocation(
                        route_id=route.id,
                        location_id=location.id,
                        order=order,
                        distance_threshold=app_settings.distance_threshold
                    )
                    db.session.add(route_location)
                    
                    # Criar RoutePoint para cada local
                    route_point = RoutePoint(
                        latitude=location.latitude,
                        longitude=location.longitude,
                        name=location.name,
                        city=location.city,
                        state=location.state,
                        order=order,
                        route_id=route.id,
                        location_id=location.id,
                        telephone=location.telephone
                    )
                    db.session.add(route_point)
            
            print("Adicionando vendedores à rota...")
            # Adicionar vendedores à rota
            if form.sellers.data:
                # Usar conjunto para evitar duplicatas
                unique_seller_ids = set([int(seller_id) for seller_id in form.sellers.data])
                for seller_id in unique_seller_ids:
                    seller = User.query.get(seller_id)
                    if seller and seller.role == 'seller' and seller.company_id == current_user.company_id:
                        print(f"Adicionando vendedor: {seller.username} (ID: {seller.id})")
                        if seller not in route.assigned_sellers.all():
                            route.assigned_sellers.append(seller)
            
            print("Finalizando transação...")
            db.session.commit()
            
            print("Rota criada com sucesso!")
            flash('Rota criada com sucesso!', 'success')
            return redirect(url_for('main.routes'))
            
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"ERRO DETALHADO: {str(e)}")
            print(traceback.format_exc())
            flash(f'Erro ao criar rota: {str(e)}', 'danger')
            return render_template('main/create_route.html', form=form, title='Criar Nova Rota')
    elif request.method == 'POST':
        # Se o formulário foi enviado mas não é válido
        print("Formulário não validou!")
        print(f"Erros: {form.errors}")
        print(f"Dados recebidos no POST: {request.form}")
        
    return render_template('main/create_route.html', form=form, title='Criar Nova Rota')

@main.route('/route/<int:route_id>')
@login_required
def view_route(route_id):
    route = Route.query.get_or_404(route_id)
    
    # Verificar permissões de acesso
    if current_user.is_admin():
        # Admin pode ver qualquer rota da empresa
        if route.company_id != current_user.company_id:
            abort(404)
    elif current_user.is_manager():
        # Gerente pode ver rotas que criou ou de vendedores que gerencia
        managed_sellers_ids = [seller.id for seller in current_user.managed_sellers]
        if route.creator_id != current_user.id and route.creator_id not in managed_sellers_ids:
            abort(404)
    else:  # Vendedor
        # Vendedor pode ver apenas rotas atribuídas a ele
        if route not in current_user.assigned_routes:
            abort(404)
    
    # Ordenar pontos por ordem
    route_points = sorted(route.points, key=lambda x: x.order)
    
    # Encontrar o próximo ponto não visitado
    next_point = next((point for point in route_points if not point.is_visited and point.order > 0), None)
    
    # Criar o mapa com os pontos da rota
    map_center = [sum([p.latitude for p in route_points]) / len(route_points) if route_points else -23.550520,
                 sum([p.longitude for p in route_points]) / len(route_points) if route_points else -46.633308]
    
    m = folium.Map(location=map_center, zoom_start=12)
    
    # Adicionar marcadores para cada ponto
    for i, point in enumerate(route_points):
        # Determinar cor e ícone do marcador
        if i == 0 or point.order == 0:  # Ponto de partida
            icon_color = 'green'
            icon_symbol = 'play'
            custom_text = "Ponto de Partida"
        elif next_point and point.id == next_point.id:  # Próximo ponto a ser visitado
            icon_color = 'orange'
            icon_symbol = 'arrow-right'
            custom_text = "Próximo Ponto"
        else:
            icon_color = 'green' if point.is_visited else 'red'
            icon_symbol = 'check' if point.is_visited else 'info-sign'
            custom_text = "Visitado" if point.is_visited else "Não visitado"
        
        popup_text = f"""
        <strong>{point.name}</strong><br>
        """
        
        if point.order != 0 and point.city and point.state:
            popup_text += f"{point.city}/{point.state}<br>"
        
        popup_text += f"Status: {custom_text}<br>"
        
        if point.order != 0 and point.is_visited and point.visited_at:
            popup_text += f"Visitado em: {point.visited_at.strftime('%d/%m/%Y %H:%M')}"
        
        # Adicionar círculo de destaque para o próximo ponto
        if next_point and point.id == next_point.id:
            folium.CircleMarker(
                location=[point.latitude, point.longitude],
                radius=20,
                color='orange',
                fill=True,
                fill_color='orange',
                fill_opacity=0.2,
                popup='Próximo ponto a ser visitado'
            ).add_to(m)
        
        folium.Marker(
            [point.latitude, point.longitude],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color=icon_color, icon=icon_symbol),
        ).add_to(m)
    
    # Adicionar traçado da rota
    if len(route_points) > 1:
        if route.route_geometry:
            # Usar a geometria OSRM se disponível
            try:
                # Decodificar a geometria polyline
                decoded_geometry = polyline.decode(route.route_geometry)
                
                # Adicionar o traçado da rota OSRM
                folium.PolyLine(
                    decoded_geometry,
                    color="blue",
                    weight=3,
                    opacity=0.8,
                    tooltip="Rota otimizada (OSRM)"
                ).add_to(m)
                
                # Adicionar estatísticas da rota como popup
                if route.route_distance and route.route_duration:
                    html = f"""
                    <div style="padding: 10px; background-color: white; border-radius: 5px; 
                               box-shadow: 0 0 10px rgba(0,0,0,0.3); max-width: 300px;">
                        <h4 style="margin: 0 0 10px 0;">Estatísticas da Rota</h4>
                        <p><b>Distância:</b> {route.route_distance/1000:.2f} km</p>
                        <p><b>Tempo estimado:</b> {route.route_duration/60:.1f} min</p>
                    </div>
                    """
                    # Posicionar o popup no ponto de partida
                    start_point = next((p for p in route_points if p.order == 0), route_points[0])
                    folium.Marker(
                        [start_point.latitude, start_point.longitude],
                        popup=folium.Popup(html, max_width=300),
                        icon=folium.DivIcon(html=f"""
                            <div style="background-color:transparent;"></div>
                        """)
                    ).add_to(m)
            except Exception as e:
                print(f"Erro ao decodificar geometria OSRM: {e}")
                # Fallback para linha reta
                coordinates = [[p.latitude, p.longitude] for p in route_points]
                folium.PolyLine(coordinates, color="red", weight=2.5, opacity=0.8).add_to(m)
        else:
            # Usar linha reta entre os pontos como fallback
            coordinates = [[p.latitude, p.longitude] for p in route_points]
            folium.PolyLine(coordinates, color="red", weight=2.5, opacity=0.8).add_to(m)
    
    # Adicionar legenda ao mapa
    legend_html = """
    <style>
       .legend {
           position: fixed;
           bottom: 20px;
           left: 20px;
           border: 2px solid grey;
           z-index: 9999;
           background-color: white;
           padding: 10px;
           border-radius: 5px;
           font-size: 14px;
       }

      @media (max-width: 768px) {
            .legend {
                font-size: 10px;
                padding: 5px;
                bottom: 10px;
                left: 10px;
            }
        }
    </style>
    <div class="legend">
       <p><strong>Legenda:</strong></p>
       <p>
           <i class="fa fa-play" style="color:green"></i> Ponto de Partida<br>
           <i class="fa fa-arrow-right" style="color:orange"></i> Próximo Ponto<br>
           <i class="fa fa-check" style="color:green"></i> Visitado<br>
           <i class="fa fa-info-sign" style="color:red"></i> Não Visitado
       </p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Salvar mapa como HTML
    map_file = f"route_map_{route.id}.html"
    map_path = os.path.join(current_app.static_folder, 'maps', map_file)
    os.makedirs(os.path.dirname(map_path), exist_ok=True)
   # Delete the old map file if it exists
    if os.path.exists(map_path):
        os.remove(map_path)

    m.save(map_path)
    
    # Formulário para completar rota
    complete_form = CompleteRouteForm()
    
    # Formulário para clonar rota concluída
    clone_form = None
    if route.is_completed:
        clone_form = CloneRouteForm()
    
    # Obter criador da rota
    creator = User.query.get(route.creator_id)
    
    # Obter vendedores atribuídos à rota
    assigned_sellers = route.assigned_sellers.all()
    
    # Adicionar timestamp para evitar cache
    timestamp = int(time.time())
    
    return render_template('main/view_route.html',
        route=route,
        points=route_points,
        map_file='maps/' + map_file,
        timestamp=timestamp,  # Adicionar timestamp
        complete_form=complete_form,
        clone_form=clone_form,
        creator=creator,
        assigned_sellers=assigned_sellers)

@main.route('/route/<int:route_id>/complete', methods=['POST'])
@login_required
def complete_route(route_id):
    route = Route.query.get_or_404(route_id)
    
    # Verificar permissões
    if current_user.is_seller() and route not in current_user.assigned_routes:
        abort(403)
    elif current_user.is_manager():
        managed_sellers_ids = [seller.id for seller in current_user.managed_sellers]
        if route.creator_id != current_user.id and route.creator_id not in managed_sellers_ids:
            abort(403)
    elif current_user.is_admin() and route.company_id != current_user.company_id:
        abort(403)
    
    form = CompleteRouteForm()
    if form.validate_on_submit() and form.confirm.data:
        route.is_completed = True
        route.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        flash(f'Rota "{route.name}" finalizada com sucesso!', 'success')
        return redirect(url_for('main.routes'))
    
    return redirect(url_for('main.view_route', route_id=route_id))

@main.route('/route/<int:route_id>/clone', methods=['POST'])
@login_required
def clone_route(route_id):
    # Apenas rotas concluídas podem ser clonadas
    original_route = Route.query.get_or_404(route_id)
    
    if not original_route.is_completed:
        flash('Apenas rotas concluídas podem ser clonadas', 'danger')
        return redirect(url_for('main.view_route', route_id=route_id))
    
    # Verificar permissões
    if current_user.is_seller():
        abort(403)  # Vendedores não podem clonar rotas
    elif current_user.is_manager():
        managed_sellers_ids = [seller.id for seller in current_user.managed_sellers]
        if original_route.creator_id != current_user.id and original_route.creator_id not in managed_sellers_ids:
            abort(403)
    elif current_user.is_admin() and original_route.company_id != current_user.company_id:
        abort(403)
    
    form = CloneRouteForm()
    if form.validate_on_submit():
        # Criar nova rota com base na original
        new_route = original_route.create_child_route()
        new_route.name = form.name.data  # Usar o nome fornecido pelo usuário
        
        db.session.add(new_route)
        db.session.flush()
        
        # Copiar pontos da rota original
        for point in original_route.points:
            new_point = RoutePoint(
                latitude=point.latitude,
                longitude=point.longitude,
                name=point.name,
                city=point.city,
                state=point.state,
                order=point.order,
                route_id=new_route.id
            )
            db.session.add(new_point)
        
        # Atribuir os mesmos vendedores
        for seller in original_route.assigned_sellers:
            new_route.assigned_sellers.append(seller)
        
        # Copiar os mesmos locais
        for location in original_route.locations:
            new_route.locations.append(location)
        
        db.session.commit()
        
        flash(f'Rota "{new_route.name}" criada com sucesso a partir da rota "{original_route.name}"!', 'success')
        return redirect(url_for('main.view_route', route_id=new_route.id))
    
    return redirect(url_for('main.view_route', route_id=route_id))

@main.route('/route/<int:route_id>/delete', methods=['POST'])
@login_required
def delete_route(route_id):
    route = Route.query.get_or_404(route_id)
    
    # Verificar permissões
    if current_user.is_seller():
        abort(403)  # Vendedores não podem excluir rotas
    elif current_user.is_manager() and route.creator_id != current_user.id:
        abort(403)  # Gerentes só podem excluir suas próprias rotas
    elif current_user.is_admin() and route.company_id != current_user.company_id:
        abort(403)  # Admin só pode excluir rotas da sua empresa
    
    # Guardar o nome para mensagem
    route_name = route.name
    
    # Remover relacionamentos
    for seller in route.assigned_sellers.all():
        route.assigned_sellers.remove(seller)
    
    # Excluir a rota
    db.session.delete(route)
    db.session.commit()
    
    flash(f'Rota "{route_name}" excluída com sucesso!', 'success')
    return redirect(url_for('main.routes'))

@main.route('/route/<int:route_id>/toggle_point/<int:point_id>', methods=['POST'])
@login_required
def toggle_point(route_id, point_id):
    """
    Endpoint legado para alternar o status de visitado de um ponto.
    Agora redireciona para a nova implementação com verificação de geolocalização.
    """
    try:
        # Verifica se o ponto existe
        point = RoutePoint.query.get_or_404(point_id)
        location_id = point.location_id
        
        # Se o ponto não estiver associado a um local, ou se for uma desmarcação, usa o comportamento antigo
        if not location_id or point.is_visited:
            # Verificar se a rota já está concluída
            route = Route.query.get_or_404(route_id)
            if route.is_completed:
                return jsonify({
                    'success': False,
                    'message': 'Esta rota já foi concluída e não pode ser modificada.'
                }), 403
            
            # Verificar permissões
            if current_user.is_admin():
                if route.company_id != current_user.company_id:
                    abort(403)
            elif current_user.is_manager():
                managed_sellers_ids = [seller.id for seller in current_user.managed_sellers]
                if route.creator_id != current_user.id and route.creator_id not in managed_sellers_ids:
                    abort(403)
            else:  # Vendedor
                if route not in current_user.assigned_routes:
                    abort(403)
            
            # Alternar o status do ponto
            if point.is_visited:
                point.mark_as_not_visited()
                message = f'Ponto "{point.name}" marcado como não visitado'
            else:
                point.mark_as_visited()
                message = f'Ponto "{point.name}" marcado como visitado'
            
            db.session.commit()
            
            # Verificar se todos os pontos foram visitados
            all_visited = all(p.is_visited for p in route.points)
            
            return jsonify({
                'success': True,
                'is_visited': point.is_visited,
                'message': message,
                'visited_at': point.visited_at.strftime('%d/%m/%Y %H:%M') if point.visited_at else None,
                'all_visited': all_visited
            })
        else:
            # Redireciona para a nova implementação com verificação de geolocalização
            return redirect(url_for('main.toggle_location_visited', route_id=route_id, location_id=location_id))
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar o status do ponto: {str(e)}'
        }), 500

@main.route('/route/<int:route_id>/email', methods=['POST'])
@login_required
def email_route(route_id):
    route = Route.query.filter_by(id=route_id, creator_id=current_user.id).first_or_404()
    points = RoutePoint.query.filter_by(route_id=route.id).order_by(RoutePoint.order).all()
    

@main.route('/routes/<int:route_id>/optimize', methods=['POST'])
@login_required
def optimize_route(route_id):
    try:
        # Verificar JSON
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'Dados JSON inválidos'}), 400
        
        # Obter token CSRF - aceitar do payload ou do header
        csrf_token = data.get('csrf_token') or request.headers.get('X-CSRFToken')
        
        # Desativar temporariamente a validação de CSRF para solucionar o problema
        # if not csrf_token or not validate_csrf(csrf_token):
        #    return jsonify({'success': False, 'message': 'Token CSRF inválido'}), 403
            
        # Obter a rota
        route = Route.query.get_or_404(route_id)
        
        # Verificar se o usuário tem permissão
        if not (current_user.is_admin() or current_user.is_manager() or 
                route.is_assigned_to(current_user) or route.creator_id == current_user.id):
            return jsonify({'success': False, 'message': 'Sem permissão para esta ação'}), 403
        
        # Verificar se a rota está concluída
        if route.is_completed:
            return jsonify({'success': False, 'message': 'Esta rota já foi concluída e não pode ser otimizada'}), 400
            
            # Marcar rota como sendo otimizada
            route.optimization_status = 'optimizing'
            db.session.commit()

            # Obter a aplicação Flask atual para usar no contexto da thread
            app_context = current_app._get_current_object()

            # Iniciar a otimização em uma thread separada
            thread = Thread(target=process_route_optimization, args=(route.id, app_context))
            thread.daemon = True  # Permite que a aplicação saia mesmo se a thread estiver rodando
            thread.start()

            # Retornar imediatamente para o usuário
            return jsonify({
                'success': True,
                'message': 'Otimização da rota iniciada em segundo plano.',
                'status': 'optimizing'
            })

    except Exception as e:
        # Se ocorrer um erro antes de iniciar a thread, reverter o status
        if route and route.optimization_status == 'optimizing':
            route.optimization_status = 'failed' # Ou 'not_optimized' dependendo da lógica desejada
            db.session.commit()
        print(f"Erro geral na rota /optimize: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Erro ao iniciar otimização: {str(e)}'}), 500

@main.route('/route/<int:route_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_route(route_id):
    route = Route.query.get_or_404(route_id)
    
    # Verificar permissões
    if current_user.is_seller():
        abort(403)  # Vendedores não podem editar rotas
    elif current_user.is_manager() and route.creator_id != current_user.id:
        abort(403)  # Gerentes só podem editar suas próprias rotas
    elif current_user.is_admin() and route.company_id != current_user.company_id:
        abort(403)  # Admin só pode editar rotas da sua empresa
    
    form = EditRouteForm(obj=route)
    
    # Preencher opções para gerentes (apenas para admin)
    if current_user.is_admin():
        managers = User.query.filter_by(company_id=current_user.company_id, role='manager').all()
        form.managers.choices = [(m.id, m.username) for m in managers]
        
        # Pré-selecionar gerentes que têm vendedores atribuídos à rota
        current_sellers = route.assigned_sellers.all()
        current_manager_ids = []
        for seller in current_sellers:
            for manager in seller.managers:
                if manager.id not in current_manager_ids:
                    current_manager_ids.append(manager.id)
        
        form.managers.data = current_manager_ids
    else:
        form.managers.choices = []
    
    # Preencher opções para vendedores
    if current_user.is_admin():
        # Admin vê todos os vendedores da empresa
        sellers = User.query.filter_by(company_id=current_user.company_id, role='seller').all()
    else:
        # Gerente vê os vendedores que gerencia
        sellers = current_user.managed_sellers.all()
    
    form.sellers.choices = [(s.id, s.username) for s in sellers]
    
    # Pré-selecionar vendedores já atribuídos
    current_seller_ids = [s.id for s in route.assigned_sellers]
    form.sellers.data = current_seller_ids
    
    if form.validate_on_submit():
        # Atualizar dados básicos da rota
        form.populate_obj(route)
        route.last_updated = datetime.now(timezone.utc)
        
        # Remover todos os vendedores atuais
        for seller in route.assigned_sellers.all():
            route.assigned_sellers.remove(seller)
        
        # Adicionar os vendedores selecionados
        if form.sellers.data:
            seller_ids = request.form.getlist('sellers')
            
            for seller_id in seller_ids:
                seller = User.query.get(int(seller_id))
                if seller and seller.role == 'seller' and seller.company_id == current_user.company_id:
                    route.assigned_sellers.append(seller)
        
        # Se for admin, processar gerentes (adicionar seus vendedores)
        if current_user.is_admin() and form.managers.data:
            for manager_id in form.managers.data:
                manager = User.query.get(int(manager_id))
                if manager and manager.role == 'manager' and manager.company_id == current_user.company_id:
                    # Adicionar vendedores gerenciados que não estão já na rota
                    for seller in manager.managed_sellers:
                        if seller not in route.assigned_sellers:
                            route.assigned_sellers.append(seller)
        
        db.session.commit()
        flash(f'Rota "{route.name}" atualizada com sucesso!', 'success')
        return redirect(url_for('main.view_route', route_id=route.id))
    
    return render_template('main/edit_route.html', form=form, route=route)

@main.route('/routes/<int:route_id>/locations/<int:location_id>/toggle_visited', methods=['POST'])
@login_required
def toggle_location_visited(route_id, location_id):
    """Marca ou desmarca um local como visitado em uma rota."""
    try:
        # Verificar se temos JSON
        if not request.is_json and request.headers.get('Content-Type') != 'application/json':
            print(f"Erro de Content-Type: {request.headers.get('Content-Type')}")
            return jsonify({
                'success': False,
                'message': 'Content-Type deve ser application/json'
            }), 415
            
        # Tentar obter os dados JSON
        data = request.get_json(silent=True) or {}
        print(f"Dados recebidos: {data}")
            
        route = Route.query.get_or_404(route_id)
        location = Location.query.get_or_404(location_id)
        
        # Verificar permissões - apenas vendedores atribuídos, gerentes ou admin podem marcar
        if not current_user.is_admin():
            if current_user.is_seller():
                # Verificar se o vendedor está atribuído a esta rota
                if current_user.id not in [seller.id for seller in route.assigned_sellers]:
                    return jsonify({
                        'success': False,
                        'message': 'Você não tem permissão para modificar esta rota.'
                    }), 403
            elif current_user.is_manager():
                # Verificar se o gerente está atribuído ou é o criador
                manager_sellers = [seller.id for seller in current_user.managed_sellers]
                route_has_manager_sellers = any(seller.id in manager_sellers for seller in route.assigned_sellers)
                if not route_has_manager_sellers and route.creator_id != current_user.id:
                    return jsonify({
                        'success': False,
                        'message': 'Você não tem permissão para modificar esta rota.'
                    }), 403
        
        # Verificar se o local faz parte da rota
        route_location = RouteLocation.query.filter_by(
            route_id=route_id, 
            location_id=location_id
        ).first_or_404()
        
        # Se tentando marcar como visitado (não é uma desmarcação), verificar a posição do usuário
        user_lat = data.get('latitude')
        user_lon = data.get('longitude')
        is_marking_visited = not route_location.is_visited
        
        if is_marking_visited:
            # Verificar se as coordenadas foram fornecidas
            if user_lat is None or user_lon is None:
                return jsonify({
                    'success': False,
                    'message': 'Coordenadas do usuário não fornecidas. Permita o acesso à sua localização.'
                }), 400
            
            # Calcular distância entre a posição do usuário e a localização
            def haversine(lat1, lon1, lat2, lon2):
                # Função para calcular a distância em metros entre dois pontos geográficos
                R = 6371000  # Raio da Terra em metros
                dLat = math.radians(lat2 - lat1)
                dLon = math.radians(lon2 - lon1)
                a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                return R * c
            
            # Calcular a distância
            distance = haversine(float(user_lat), float(user_lon), location.latitude, location.longitude)
            
            # Verificar se o usuário está dentro do limite de distância
            # Usar o threshold específico da rota ou o threshold global se não definido
            threshold = route_location.distance_threshold
            if threshold is None or threshold <= 0:
                threshold = app_settings.distance_threshold
                
            if distance > threshold:
                return jsonify({
                    'success': False,
                    'message': f'Você está muito longe do local ({int(distance)}m). É necessário estar a menos de {threshold}m para marcar como visitado.',
                    'distance': int(distance),
                    'threshold': threshold
                }), 400
        
        # Se está desmarcando OU está próximo o suficiente, alterna o status visitado
        route_location.is_visited = not route_location.is_visited
        route_location.visited_at = datetime.now(timezone.utc) if route_location.is_visited else None
        route_location.visited_by_id = current_user.id if route_location.is_visited else None
        
        # Também precisamos atualizar o RoutePoint correspondente
        route_point = RoutePoint.query.filter_by(
            route_id=route_id,
            location_id=location_id
        ).first()
        
        if route_point:
            if route_location.is_visited:
                route_point.mark_as_visited()
            else:
                route_point.mark_as_not_visited()
        
        # Se todos os locais foram visitados, marcar a rota como concluída
        if route_location.is_visited:
            all_locations = RouteLocation.query.filter_by(route_id=route_id).all()
            if all(loc.is_visited for loc in all_locations):
                route.is_completed = True
                route.completed_at = datetime.now(timezone.utc)
        else:
            # Se algum local foi desmarcado, a rota não está mais concluída
            route.is_completed = False
            route.completed_at = None
        
        db.session.commit()
        
        # Incluir distância nas informações de retorno, se disponíveis
        response_data = {
            'success': True, 
            'visited': route_location.is_visited,
            'route_completed': route.is_completed
        }
        
        if is_marking_visited:
            response_data['distance'] = int(distance)
            response_data['threshold'] = threshold
        
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Erro ao processar toggle_location_visited: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar o status do local: {str(e)}'
        }), 500

@main.route('/route/<int:route_id>/optimization-status', methods=['GET'])
@login_required
def get_optimization_status(route_id):
    try:
        route = Route.query.get_or_404(route_id)
        
        # Verificar permissões
        if route.company_id != current_user.company_id:
            return jsonify({'success': False, 'message': 'Você não tem permissão para acessar esta rota.'}), 403
        
        # Retornar o status atual
        status = {
            'success': True,
            'status': route.optimization_status,
            'is_optimized': route.is_optimized,
        }
        
        # Adicionar informações adicionais se estiver otimizado
        if route.is_optimized and route.optimized_at:
            status['optimized_at'] = route.optimized_at.strftime('%d/%m/%Y %H:%M')
            
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Página de configurações do sistema"""
    # Apenas administradores podem acessar as configurações
    if not current_user.is_admin():
        flash('Acesso negado. Apenas administradores podem acessar as configurações do sistema.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Atualizar configurações
        try:
            # Validar distância
            distance_threshold = int(request.form.get('distance_threshold', 100))
            if distance_threshold < 10 or distance_threshold > 1000:
                flash('A distância deve estar entre 10 e 1000 metros.', 'warning')
                distance_threshold = 100  # Valor padrão se inválido
            
            # Atualizar configuração global
            app_settings.distance_threshold = distance_threshold
            
            # Verificar se deve aplicar às rotas existentes
            apply_to_existing = 'apply_to_existing' in request.form
            
            if apply_to_existing:
                # Atualizar todas as rotas da empresa do usuário
                route_locations = RouteLocation.query.join(Route).filter(
                    Route.company_id == current_user.company_id
                ).all()
                
                for rl in route_locations:
                    rl.distance_threshold = distance_threshold
                
                db.session.commit()
                flash(f'Configurações atualizadas e aplicadas a {len(route_locations)} locais de rotas existentes.', 'success')
            else:
                flash('Configurações atualizadas com sucesso. Serão aplicadas a novas rotas.', 'success')
            
            return redirect(url_for('main.settings'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar configurações: {str(e)}', 'danger')
    
    # Preparar dados para exibição
    current_settings = {
        'distance_threshold': app_settings.distance_threshold
    }
    
    return render_template('main/settings.html', current_settings=current_settings)

@main.route('/route/<int:route_id>/change_starting_point', methods=['POST'])
@login_required
def change_starting_point(route_id):
    """Altera o ponto de partida de uma rota."""
    try:
        route = Route.query.get_or_404(route_id)
        
        # Verificar permissões
        if current_user.is_seller() and route not in current_user.assigned_sellers:
            return jsonify({
                'success': False,
                'message': 'Você não tem permissão para modificar esta rota.'
            }), 403
        elif current_user.is_manager():
            managed_sellers_ids = [seller.id for seller in current_user.managed_sellers]
            if route.creator_id != current_user.id and not any(seller.id in managed_sellers_ids for seller in route.assigned_sellers):
                return jsonify({
                    'success': False,
                    'message': 'Você não tem permissão para modificar esta rota.'
                }), 403
        elif current_user.is_admin() and route.company_id != current_user.company_id:
            return jsonify({
                'success': False,
                'message': 'Você não tem permissão para modificar esta rota.'
            }), 403
            
        # Verificar se a rota está concluída
        if route.is_completed:
            return jsonify({
                'success': False,
                'message': 'Não é possível modificar o ponto de partida de uma rota concluída.'
            }), 400
        
        # Obter dados do request
        data = request.get_json()
        start_point_type = data.get('type')
        
        if start_point_type not in ['geolocation', 'manual']:
            return jsonify({
                'success': False,
                'message': 'Tipo de ponto de partida inválido.'
            }), 400
            
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        point_name = data.get('name', 'Ponto de Partida')
        
        if latitude is None or longitude is None:
            return jsonify({
                'success': False,
                'message': 'Coordenadas não fornecidas.'
            }), 400
            
        # Encontrar o ponto de partida atual (ordem 0)
        existing_start_point = RoutePoint.query.filter_by(route_id=route.id, order=0).first()
        
        if existing_start_point:
            # Atualizar o ponto de partida existente
            existing_start_point.latitude = latitude
            existing_start_point.longitude = longitude
            existing_start_point.name = point_name
            existing_start_point.city = ''  # Limpar cidade
            existing_start_point.state = ''  # Limpar estado
            existing_start_point.is_visited = False  # Resetar status de visitado
            existing_start_point.visited_at = None
        else:
            # Criar um novo ponto de partida
            new_start_point = RoutePoint(
                route_id=route.id,
                latitude=latitude,
                longitude=longitude,
                name=point_name,
                city='',
                state='',
                order=0,
            )
            db.session.add(new_start_point)
        
        # Se a rota estiver otimizada, precisamos resetar o status
        was_optimized = route.is_optimized
        route.is_optimized = False
        route.optimized_at = None
        route.optimization_status = 'not_optimized'
        route.last_updated = datetime.now(timezone.utc)
        
        db.session.commit()
        
        # Verificar se deve otimizar (sempre respeitando a opção do usuário)
        should_optimize = data.get('optimize', False)
        
        # Se deve otimizar, iniciar otimização
        if should_optimize:
            # Iniciar otimização da rota
            route.mark_as_optimizing()
            
            # Obter a aplicação Flask atual para usar no contexto
            app = current_app._get_current_object()
            
            # Iniciar otimização em processo separado
            thread = Thread(target=process_route_optimization, args=(route.id, app))
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': 'Ponto de partida alterado e rota em otimização.',
                'optimize_started': True,
                'status': 'optimizing'
            })
        
        return jsonify({
            'success': True,
            'message': 'Ponto de partida alterado com sucesso.',
            'status': 'not_optimized'
        })
    
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Erro ao alterar ponto de partida: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Erro ao alterar ponto de partida: {str(e)}'
        }), 500

@main.route('/routes/<int:route_id>/locations/<int:location_id>/check-in', methods=['POST'])
@login_required
def location_check_in(route_id, location_id):
    try:
        # Verificar JSON
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'Dados JSON inválidos'}), 400
        
        # Obter token CSRF - aceitar do payload ou do header
        csrf_token = data.get('csrf_token') or request.headers.get('X-CSRFToken')
        print(f"Token CSRF recebido: {csrf_token}")
        
        # Desativar temporariamente a validação de CSRF para solucionar o problema
        # if not csrf_token or not validate_csrf(csrf_token):
        #    return jsonify({'success': False, 'message': 'Token CSRF inválido'}), 403
            
        # Obter a rota
        route = Route.query.get_or_404(route_id)
        
        # Verificar se o usuário tem permissão
        if not (current_user.is_admin() or current_user.is_manager() or 
                route.is_assigned_to(current_user) or route.creator_id == current_user.id):
            return jsonify({'success': False, 'message': 'Sem permissão para esta ação'}), 403
        
        # Verificar se a rota está concluída
        if route.is_completed:
            return jsonify({'success': False, 'message': 'Esta rota já foi concluída'}), 400
        
        # Obter o location
        location = Location.query.get_or_404(location_id)
        
        # Encontrar o route_location correspondente
        route_location = RouteLocation.query.filter_by(
            route_id=route.id,
            location_id=location.id
        ).first()
        
        if not route_location:
            return jsonify({'success': False, 'message': 'Local não encontrado nesta rota'}), 404
        
        # Verificar se já fez check-in
        if route_location.check_in_at:
            return jsonify({'success': False, 'message': 'Check-in já realizado para este local'}), 400
        
        # Verificar geolocalização
        user_lat = data.get('latitude')
        user_lon = data.get('longitude')
        
        if not user_lat or not user_lon:
            return jsonify({'success': False, 'message': 'Dados de localização inválidos'}), 400
        
        # Converter para float
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Coordenadas inválidas'}), 400
        
        # Calcular distância (em metros) usando Haversine
        distance = haversine(user_lat, user_lon, location.latitude, location.longitude)
        
        # Verificar se está dentro do limite de distância
        if distance > route_location.distance_threshold:
            return jsonify({
                'success': False, 
                'message': f'Você está a {distance:.0f}m do local. Aproxime-se para fazer check-in (limite: {route_location.distance_threshold}m)'
            }), 400
        
        # Registrar check-in
        route_location.check_in_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Check-in realizado com sucesso! (Distância: {distance:.0f}m)',
            'check_in_at': route_location.check_in_at.strftime('%H:%M:%S'),
            'distance': int(distance)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro no check-in: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao processar check-in: {str(e)}'}), 500

@main.route('/routes/<int:route_id>/locations/<int:location_id>/check-out', methods=['POST'])
@login_required
def location_check_out(route_id, location_id):
    try:
        # Verificar JSON
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'Dados JSON inválidos'}), 400
        
        # Obter token CSRF - aceitar do payload ou do header
        csrf_token = data.get('csrf_token') or request.headers.get('X-CSRFToken')
        print(f"Token CSRF (check-out) recebido: {csrf_token}")
        
        # Desativar temporariamente a validação de CSRF para solucionar o problema
        # if not csrf_token or not validate_csrf(csrf_token):
        #    return jsonify({'success': False, 'message': 'Token CSRF inválido'}), 403
            
        # Obter a rota
        route = Route.query.get_or_404(route_id)
        
        # Verificar se o usuário tem permissão
        if not (current_user.is_admin() or current_user.is_manager() or 
                route.is_assigned_to(current_user) or route.creator_id == current_user.id):
            return jsonify({'success': False, 'message': 'Sem permissão para esta ação'}), 403
        
        # Verificar se a rota está concluída
        if route.is_completed:
            return jsonify({'success': False, 'message': 'Esta rota já foi concluída'}), 400
        
        # Obter o location
        location = Location.query.get_or_404(location_id)
        
        # Encontrar o route_location correspondente
        route_location = RouteLocation.query.filter_by(
            route_id=route.id,
            location_id=location.id
        ).first()
        
        if not route_location:
            return jsonify({'success': False, 'message': 'Local não encontrado nesta rota'}), 404
        
        # Verificar se já fez check-in
        if not route_location.check_in_at:
            return jsonify({'success': False, 'message': 'É necessário fazer check-in antes do check-out'}), 400
        
        # Verificar se já fez check-out
        if route_location.check_out_at:
            return jsonify({'success': False, 'message': 'Check-out já realizado para este local'}), 400
        
        # Registrar check-out
        route_location.check_out_at = datetime.now(timezone.utc)
        
        # Marcar o ponto como visitado no RoutePoint
        route_point = RoutePoint.query.filter_by(
            route_id=route_id,
            location_id=location_id
        ).first()
        
        if route_point:
            route_point.mark_as_visited()
        
        # Verificar se todos os pontos foram visitados para marcar a rota como concluída
        all_points = RoutePoint.query.filter_by(route_id=route_id).all()
        if all(point.is_visited for point in all_points if point.order > 0):  # ignorar ponto de partida
            route = Route.query.get(route_id)
            route.is_completed = True
            route.completed_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Check-out realizado com sucesso!',
            'check_out_at': route_location.check_out_at.strftime('%H:%M:%S')
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro no check-out: {str(e)}")

        return jsonify({'success': False, 'message': f'Erro ao processar check-out: {str(e)}'}), 500

def process_route_optimization(route_id, app):
    """
    Função para processar a otimização da rota em background
    """
    with app.app_context():
        try:
            # Obter a rota
            route = Route.query.get(route_id)
            if not route:
                print(f"Rota {route_id} não encontrada")
                return

            # Obter todos os pontos da rota
            route_points = RoutePoint.query.filter_by(route_id=route_id).all()
            
            # Separar o ponto de partida dos outros pontos
            starting_point = None
            points_for_optimization = []
            
            for point in route_points:
                if point.order == 0:
                    starting_point = (point.latitude, point.longitude)
                else:
                    points_for_optimization.append({
                        'latitude': point.latitude,
                        'longitude': point.longitude,
                        'id': point.id,
                        'nome': point.name,
                        'cidade': point.city or ""
                    })

            # Importar função de otimização
            from appReta import optimize_route as app_optimize_route
            
            # Executar otimização
            optimization_result = app_optimize_route(points_for_optimization, starting_point)
            
            if optimization_result:
                optimized_points = optimization_result['points']
                osrm_data = optimization_result.get('osrm_data')
                
                # Atualizar ordem dos pontos
                for i, opt_point in enumerate(optimized_points, 1):
                    point_id = opt_point['id']
                    point = next((p for p in route_points if p.id == point_id), None)
                    if point:
                        point.order = i

                # Atualizar dados OSRM se disponíveis
                if osrm_data and osrm_data.get('success'):
                    route.route_geometry = osrm_data['geometry_encoded']
                    route.route_duration = osrm_data['duration']
                    route.route_distance = osrm_data['distance']

                # Atualizar status da rota
                route.is_optimized = True
                route.optimized_at = datetime.now(timezone.utc)
                route.optimization_status = 'optimized'
                db.session.commit()
            else:
                route.optimization_status = 'failed'
                db.session.commit()

        except Exception as e:
            print(f"Erro na otimização assíncrona: {str(e)}")
            route.optimization_status = 'failed'
            db.session.commit()        

@main.route('/templates')
@login_required
def route_templates():
    # Vendedores não têm acesso
    if current_user.is_seller():
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Base query para templates da empresa
    query = Route.query.filter_by(
        company_id=current_user.company_id,
        is_template=True
    )
    
    # Se for gerente, filtrar apenas templates próprios
    if current_user.is_manager():
        query = query.filter_by(creator_id=current_user.id)
    
    templates = query.order_by(Route.created_at.desc()).all()
    
    return render_template('main/route_templates.html', templates=templates)

@main.route('/templates/<int:template_id>/points')
@login_required
def get_template_points(template_id):
    try:
        template = Route.query.get_or_404(template_id)
        points = RoutePoint.query.filter_by(route_id=template_id).order_by(RoutePoint.order).all()
        
        return jsonify({
            'success': True,
            'points': [{
                'id': point.id,
                'order': point.order,
                'name': point.name,
                'city': point.city,
                'state': point.state,
                'location_id': point.location_id
            } for point in points]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/locations/available')
@login_required
def get_available_locations():
    try:
        locations = Location.query.filter_by(company_id=current_user.company_id).all()
        return jsonify({
            'success': True,
            'locations': [{
                'id': loc.id,
                'name': loc.name,
                'city': loc.city,
                'state': loc.state
            } for loc in locations]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/templates/<int:template_id>/points', methods=['POST'])
@login_required
def add_template_point(template_id):
    try:
        data = request.get_json()
        location_id = data.get('location_id')
        
        template = Route.query.get_or_404(template_id)
        location = Location.query.get_or_404(location_id)
        
        # Verificar se o local já existe na rota
        existing_point = RoutePoint.query.filter_by(
            route_id=template_id,
            location_id=location_id
        ).first()
        
        if existing_point:
            return jsonify({
                'success': False,
                'message': 'Este local já está na rota'
            }), 400
        
        # Pegar a próxima ordem disponível
        max_order = db.session.query(func.max(RoutePoint.order))\
            .filter_by(route_id=template_id).scalar() or 0
        
        new_point = RoutePoint(
            route_id=template_id,
            location_id=location_id,
            latitude=location.latitude,    # Adicione estas
            longitude=location.longitude,  # coordenadas
            name=location.name,
            city=location.city,
            state=location.state,
            telephone=location.telephone,  # Adicionando o telefone
            order=max_order + 1
        )
        
        db.session.add(new_point)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/templates/<int:template_id>/points/<int:point_id>', methods=['DELETE'])
@login_required
def remove_template_point(template_id, point_id):
    try:
        # Verificar se o template pertence à empresa do usuário
        template = Route.query.get_or_404(template_id)
        if template.company_id != current_user.company_id:
            return jsonify({
                'success': False,
                'message': 'Você não tem permissão para modificar este template'
            }), 403
            
        point = RoutePoint.query.get_or_404(point_id)
        
        # Verificar se o ponto pertence ao template
        if point.route_id != template_id:
            return jsonify({
                'success': False,
                'message': 'Este ponto não pertence ao template especificado'
            }), 400
            
        db.session.delete(point)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/routes/<int:route_id>/save-template', methods=['POST'])
@login_required
def save_as_template(route_id):
    try:
        route = Route.query.get_or_404(route_id)
        
        if current_user.company_id != route.company_id:
            return jsonify({
                'success': False, 
                'message': 'Você não tem permissão para salvar esta rota como template.'
            }), 403
        
        if route.is_template:
            return jsonify({
                'success': False, 
                'message': 'Esta rota já é um template.'
            }), 400
            
        # Criar novo template
        template = Route(
            name=f"Template - {route.name}",
            description=route.description,
            company_id=current_user.company_id,
            creator_id=current_user.id,
            is_template=True,
            is_optimized=False,
            optimization_status=None,
            # Resetar dados de rota OSRM
            route_geometry=None,
            route_duration=None,
            route_distance=None,
            is_completed=None,
            completed_at=None           
        )
        
        db.session.add(template)
        db.session.flush()
        
        # Copiar locations do template com suas configurações
        for rl in route.route_locations:
            new_rl = RouteLocation(
                route_id=template.id,
                location_id=rl.location_id,
                order=rl.order,
                distance_threshold=rl.distance_threshold,
                # Não copiar check_in_at e check_out_at pois são específicos de cada visita
            )
            db.session.add(new_rl)
            
            # Criar route_point correspondente
            location = Location.query.get(rl.location_id)
            if location:
                new_point = RoutePoint(
                    route_id=template.id,
                    location_id=rl.location_id,  # Importante: associar o location_id
                    latitude=location.latitude,
                    longitude=location.longitude,
                    name=location.name,
                    city=location.city,
                    state=location.state,
                    order=rl.order
                )
                db.session.add(new_point)
        
        # Copiar vendedores atribuídos
        for seller in route.assigned_sellers:
            template.assigned_sellers.append(seller)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Rota salva como template com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao salvar template: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar template: {str(e)}'
        }), 500

@main.route('/templates/<int:template_id>/create-route', methods=['POST'])
@login_required
def create_route_from_template(template_id):
    """Cria uma nova rota a partir de um template"""
    try:
        template = Route.query.get_or_404(template_id)
        
        # Verificar permissões e status do template
        if template.company_id != current_user.company_id or not template.is_template:
            return jsonify({
                'success': False,
                'message': 'Você não tem permissão para usar este template.'
            }), 403
        
        # Obter o nome da nova rota do request
        data = request.get_json()
        new_name = data.get('name')
        
        if not new_name:
            return jsonify({
                'success': False,
                'message': 'Nome da rota é obrigatório.'
            }), 400
        
        # Criar nova rota
        new_route = Route(
            name=new_name,  # Usar o nome fornecido pelo usuário
            description=template.description,
            company_id=current_user.company_id,
            creator_id=current_user.id,
            is_template=False,
            is_optimized=template.is_optimized,
            optimization_status=template.optimization_status,
            parent_template_id=template.id
        )
        
        db.session.add(new_route)
        db.session.flush()  # Obtém o ID da nova rota
        
        # Obter todos os pontos do template ordenados
        template_points = RoutePoint.query.filter_by(
            route_id=template_id
        ).order_by(RoutePoint.order).all()
        
        # Copiar os pontos do template para a nova rota
        for point in template_points:
            # Criar route_point
            new_point = RoutePoint(
                route_id=new_route.id,
                location_id=point.location_id,
                latitude=point.latitude,
                longitude=point.longitude,
                name=point.name,
                city=point.city,
                state=point.state,
                telephone=point.telephone,  # Adicionando o telefone
                order=point.order
            )
            db.session.add(new_point)
            
            # Se o ponto tem um location_id, criar também o RouteLocation
            if point.location_id:
                new_rl = RouteLocation(
                    route_id=new_route.id,
                    location_id=point.location_id,
                    order=point.order,
                    distance_threshold=app_settings.distance_threshold
                )
                db.session.add(new_rl)
        
        # Copiar vendedores atribuídos
        for seller in template.assigned_sellers:
            new_route.assigned_sellers.append(seller)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Nova rota criada com sucesso!',
            'redirect_url': url_for('main.view_route', route_id=new_route.id)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar rota do template: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao criar rota: {str(e)}'
        }), 500

@main.route('/templates/<int:template_id>/delete', methods=['POST'])
@login_required
def delete_template(template_id):
    try:
        template = Route.query.get_or_404(template_id)
        
        # Verificar permissões
        if not (current_user.is_admin() or template.creator_id == current_user.id):
            return jsonify({
                'success': False,
                'message': 'Você não tem permissão para excluir este template.'
            }), 403
            
        # Verificar se é realmente um template
        if not template.is_template:
            return jsonify({
                'success': False,
                'message': 'Este item não é um template.'
            }), 400
            
        # Excluir template
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Template excluído com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao excluir template: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir template: {str(e)}'
        }), 500

@main.route('/routes/<int:route_id>/change-starting-point', methods=['POST'])
@login_required
def update_starting_point(route_id):
    try:
        # Verificar JSON
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'Dados JSON inválidos'}), 400
        
        # Obter dados do novo ponto de partida
        latitude = float(data.get('latitude', 0))
        longitude = float(data.get('longitude', 0))
        name = data.get('name', 'Ponto de Partida')
        optimize = data.get('optimize', False)
        
        if latitude == 0 or longitude == 0:
            return jsonify({'success': False, 'message': 'Coordenadas inválidas'}), 400
        
        # Obter a rota
        route = Route.query.get_or_404(route_id)
        
        # Verificar se o usuário tem permissão
        if not (current_user.is_admin() or current_user.is_manager() or 
                route.is_assigned_to(current_user) or route.creator_id == current_user.id):
            return jsonify({'success': False, 'message': 'Sem permissão para esta ação'}), 403
        
        # Verificar se a rota está concluída
        if route.is_completed:
            return jsonify({'success': False, 'message': 'Esta rota já foi concluída e não pode ser alterada'}), 400
        
        # Verificar se já existe um ponto de partida (ordem 0)
        existing_start = RoutePoint.query.filter_by(route_id=route_id, order=0).first()
        
        if existing_start:
            # Atualizar ponto de partida existente
            existing_start.latitude = latitude
            existing_start.longitude = longitude
            existing_start.name = name
            db.session.commit()
            
            print(f"Ponto de partida atualizado: ID {existing_start.id}, Coordenadas: {latitude}, {longitude}")
            message = "Ponto de partida atualizado com sucesso"
        else:
            # Criar novo ponto de partida
            new_start = RoutePoint(
                route_id=route_id,
                latitude=latitude,
                longitude=longitude,
                name=name,
                order=0
            )
            db.session.add(new_start)
            db.session.commit()
            
            print(f"Novo ponto de partida criado: ID {new_start.id}, Coordenadas: {latitude}, {longitude}")
            message = "Novo ponto de partida criado com sucesso"
        
        # Otimizar a rota se solicitado
        if optimize:
            # Marcar para otimização
            route.optimization_status = 'optimizing'
            db.session.commit()
            
            # Executar otimização em segundo plano (chamar endpoint de otimização)
            try:
                # Importar funções do appReta
                from appReta import optimize_route as app_optimize_route
                
                # Obter todos os pontos da rota
                route_points = RoutePoint.query.filter_by(route_id=route_id).all()
                
                if len(route_points) >= 3:  # Precisamos de pelo menos 3 pontos para otimizar
                    # Separar o ponto de partida dos outros pontos
                    other_points = [rp for rp in route_points if rp.order != 0]
                    
                    # Preparar pontos no formato esperado pelo algoritmo de otimização
                    points_for_optimization = []
                    for point in other_points:
                        points_for_optimization.append({
                            'latitude': point.latitude, 
                            'longitude': point.longitude,
                            'id': point.id,
                            'nome': point.name,
                            'cidade': point.city or ""
                        })
                    
                    # Executar a otimização com o novo ponto de partida
                    partida_otimizacao = (latitude, longitude)
                    optimization_result = app_optimize_route(points_for_optimization, partida_otimizacao)
                    optimized_points = optimization_result['points']
                    osrm_data = optimization_result['osrm_data']
                    
                    # Atualizar a ordem dos pontos baseado no resultado
                    for i, opt_point in enumerate(optimized_points, 1):
                        point_id = opt_point['id']
                        point = next((p for p in route_points if p.id == point_id), None)
                        if point:
                            point.order = i
                    
                    # Armazenar os dados da rota OSRM no banco
                    if osrm_data and osrm_data['success']:
                        route.route_geometry = osrm_data['geometry_encoded']
                        route.route_duration = osrm_data['duration']
                        route.route_distance = osrm_data['distance']
                    
                    # Marcar a rota como otimizada
                    route.is_optimized = True
                    route.optimized_at = datetime.now(timezone.utc)
                    route.optimization_status = 'optimized'
                    db.session.commit()
                    
                    print(f"Rota otimizada com sucesso após mudar ponto de partida")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Rota otimizada com sucesso',
                        'has_osrm_data': osrm_data['success'] if osrm_data else False,
                        'redirect': url_for('main.view_route', route_id=route_id)
                    })
                    
                else:
                    print(f"Não há pontos suficientes para otimizar (mínimo de 3 pontos)")
                    route.optimization_status = 'not_optimized'
                    db.session.commit()
                    return jsonify({'success': False, 'message': 'São necessários pelo menos 3 pontos para otimizar'}), 400
            
            except Exception as e:
                print(f"Erro ao otimizar rota: {str(e)}")
                route.optimization_status = 'failed'
                db.session.commit()
                return jsonify({'success': False, 'message': f'Erro ao otimizar rota: {str(e)}'}), 500
        
        # Se não foi solicitada otimização, retornar sucesso
        return jsonify({
            'success': True, 
            'message': message,
            'redirect': url_for('main.view_route', route_id=route_id)
        })
    
    except Exception as e:
        print(f"Erro ao atualizar ponto de partida: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@main.route('/routes/<int:route_id>/stats', methods=['GET'])
@login_required
def route_stats(route_id):
    """Retorna estatísticas da rota incluindo tempos de trabalho e deslocamento"""
    try:
        route = Route.query.get_or_404(route_id)
        
        # Verificar permissões
        if not current_user.is_admin():
            if current_user.is_seller():
                if current_user.id not in [seller.id for seller in route.assigned_sellers]:
                    abort(403)
            elif current_user.is_manager():
                manager_sellers = [seller.id for seller in current_user.managed_sellers]
                route_has_manager_sellers = any(seller.id in manager_sellers for seller in route.assigned_sellers)
                if not route_has_manager_sellers and route.creator_id != current_user.id:
                    abort(403)
        
        # Calcular estatísticas
        avg_work_time = route.get_avg_work_time()
        avg_transit_time = route.get_avg_transit_time()
        total_work_time = route.get_total_work_time()
        total_transit_time = route.get_total_transit_time()
        
        # Informações detalhadas por local
        locations_data = []
        
        # Primeiro, criar um dicionário de pontos ordenados para referência rápida
        points_by_location = {
            point.location_id: point.order 
            for point in route.points
        }
        
        # Usar os route_locations mas ordenar pela ordem dos points
        route_locations = route.route_locations
        ordered_locations = sorted(
            route_locations, 
            key=lambda rl: points_by_location.get(rl.location_id, 0)
        )
        
        for i, rl in enumerate(ordered_locations):
            if not rl.check_in_at:
                continue
                
            location_data = {
                'id': rl.location_id,
                'name': rl.location.name,
                'order': points_by_location.get(rl.location_id, 0),  # Usar a ordem do point
                'check_in_at': rl.check_in_at.strftime('%d/%m/%Y %H:%M:%S') if rl.check_in_at else None,
                'check_out_at': rl.check_out_at.strftime('%d/%m/%Y %H:%M:%S') if rl.check_out_at else None,
                'work_time': rl.get_work_time() or 0,
                'transit_time': 0  # Inicializa com 0 em vez de None
            }
            
            # Calcular tempo de trânsito se não for o primeiro local
            if i > 0 and ordered_locations[i-1].check_out_at:
                location_data['transit_time'] = rl.get_transit_time_from_previous(ordered_locations[i-1]) or 0
                
            locations_data.append(location_data)
        
        return jsonify({
            'success': True,
            'route_name': route.name,
            'avg_work_time': avg_work_time,
            'avg_transit_time': avg_transit_time,
            'total_work_time': total_work_time,
            'total_transit_time': total_transit_time,
            'locations': locations_data
        })
        
    except Exception as e:
        import traceback
        print(f"Erro ao obter estatísticas da rota: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Erro ao obter estatísticas da rota: {str(e)}'
        }), 500

@main.route('/routes/<int:route_id>/detailed_stats')
@login_required
def route_detailed_stats(route_id):
    """Renderiza a página de estatísticas detalhadas da rota."""
    route = Route.query.get_or_404(route_id)
    
    # Verificar permissões
    if not current_user.is_admin():
        if current_user.is_seller():
            if current_user.id not in [seller.id for seller in route.assigned_sellers]:
                abort(403)
        elif current_user.is_manager():
            manager_sellers = [seller.id for seller in current_user.managed_sellers]
            route_has_manager_sellers = any(seller.id in manager_sellers for seller in route.assigned_sellers)
            if not route_has_manager_sellers and route.creator_id != current_user.id:
                abort(403)
    
    return render_template('main/route_stats.html', route=route)

@main.route('/seller_stats/<int:seller_id>')
@login_required
def seller_stats(seller_id):
    """Página de estatísticas do vendedor"""
    # Verificar permissões
    if not current_user.is_admin():
        if current_user.is_seller() and current_user.id != seller_id:
            abort(403)
        elif current_user.is_manager():
            if seller_id not in [s.id for s in current_user.managed_sellers]:
                abort(403)
    
    seller = User.query.get_or_404(seller_id)
    if not seller.is_seller():
        abort(404)
    
    # Obter todas as rotas do vendedor
    routes = seller.assigned_routes.order_by(Route.created_at.desc()).all()
    
    # Calcular estatísticas''
    total_routes = len(routes)
    completed_routes = len([r for r in routes if r.is_completed])
    active_routes = total_routes - completed_routes
    
    # Médias de tempo
    total_work_time = sum(route.get_total_work_time() for route in routes)
    total_transit_time = sum(route.get_total_transit_time() for route in routes)
    avg_work_time = total_work_time / total_routes if total_routes > 0 else 0
    avg_transit_time = total_transit_time / total_routes if total_routes > 0 else 0
    
    # Calcular taxa de conclusão diária
    completion_rate = (completed_routes / total_routes * 100) if total_routes > 0 else 0
    
    return render_template('main/seller_stats.html',
                         seller=seller,
                         total_routes=total_routes,
                         completed_routes=completed_routes,
                         active_routes=active_routes,
                         avg_work_time=round(avg_work_time, 1),
                         avg_transit_time=round(avg_transit_time, 1),
                         completion_rate=round(completion_rate, 1),
                         routes=routes)

@main.route('/sellers/statistics')
@login_required
def sellers_statistics():
    """Página de listagem de vendedores para visualização de estatísticas"""
    if current_user.is_seller():
        # Vendedores são redirecionados para sua própria página de estatísticas
        return redirect(url_for('main.seller_stats', seller_id=current_user.id))
    
    # Para admin e gerentes
    if current_user.is_admin():
        # Admin vê todos os vendedores da empresa
        sellers = User.query.filter_by(
            company_id=current_user.company_id,
            role='seller'
        ).order_by(User.username).all()
    else:  # Gerente
        # Gerente vê apenas seus vendedores
        sellers = current_user.managed_sellers.order_by(User.username).all()
    
    # Calcular estatísticas básicas para cada vendedor
    sellers_stats = []
    for seller in sellers:
        routes = seller.assigned_routes.all()
        total_routes = len(routes)
        completed_routes = len([r for r in routes if r.is_completed])
        
        sellers_stats.append({
            'seller': seller,
            'total_routes': total_routes,
            'completed_routes': completed_routes,
            'completion_rate': (completed_routes / total_routes * 100) if total_routes > 0 else 0
        })
    
    return render_template(
        'main/sellers_statistics.html',
        sellers_stats=sellers_stats
    )
