
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort

db = SQLAlchemy()

# Tabela de associação para relações entre gerentes e vendedores
manager_sellers = db.Table('manager_sellers',
    db.Column('manager_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('seller_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

# Tabela de associação para atribuir rotas a vendedores
route_sellers = db.Table('route_sellers',
    db.Column('route_id', db.Integer, db.ForeignKey('routes.id'), primary_key=True),
    db.Column('seller_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    name = db.Column(db.String(100), nullable=True)
    is_super = db.Column(db.Boolean, default=False)
    
    # Novos campos para hierarquia
    role = db.Column(db.String(20), nullable=False, default='seller')  # 'admin', 'manager', 'seller'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    
    # Manter apenas a restrição composta
    __table_args__ = (
        db.UniqueConstraint('username', 'company_id', name='unique_username_per_company'),
    )
    
    # Relações
    routes = db.relationship('Route', backref='creator', lazy=True, foreign_keys='Route.creator_id')
    locations = db.relationship('Location', backref='creator', lazy=True, foreign_keys='Location.creator_id')
    
    # Relacionamentos hierárquicos
    managed_sellers = db.relationship(
        'User', secondary=manager_sellers,
        primaryjoin=(id == manager_sellers.c.manager_id),
        secondaryjoin=(id == manager_sellers.c.seller_id),
        backref=db.backref('managers', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # Rotas atribuídas ao vendedor
    assigned_routes = db.relationship(
        'Route', secondary=route_sellers,
        backref=db.backref('assigned_sellers', lazy='dynamic'),
        lazy='dynamic'
    )
    
    @property
    def display_name(self):
        """Retorna o nome do usuário ou username se o nome não estiver definido"""
        return self.name or self.username
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_manager(self):
        return self.role == 'manager'
    
    def is_seller(self):
        return self.role == 'seller'
    
    def can_create_route(self):
        """Verifica se o usuário pode criar rotas (admin ou gerente)"""
        return self.role in ['admin', 'manager']
    
    def is_super_admin(self):
        """Verifica se o usuário é um super admin"""
        return self.is_super

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Novos campos para controle de plano
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    plan_started_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relações existentes
    users = db.relationship('User', backref='company', lazy=True)
    
    @property
    def plan_expires_at(self):
        """Retorna a data de expiração do plano, ou None se for ilimitado"""
        if not self.plan.duration_days:
            return None
        return self.plan_started_at + timedelta(days=self.plan.duration_days)
    
    @property
    def is_plan_expired(self):
        """Verifica se o plano está expirado"""
        if not self.plan.duration_days:
            return False
        return datetime.now(timezone.utc) > self.plan_expires_at
    
    def check_access(self):
        """Verifica se a empresa tem acesso ao sistema"""
        return self.is_active and not self.is_plan_expired

class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    telephone = db.Column(db.String(20), nullable=True)  # Campo de telefone (não obrigatório)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Campos atualizados
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    street = db.Column(db.String(200), nullable=True)  # Nova coluna para rua
    number = db.Column(db.String(20), nullable=True)   # Nova coluna para número
    
    # Relações
    company = db.relationship('Company', backref='locations')
    routes = db.relationship(
        'Route',
        secondary='route_locations',
        viewonly=True
    )

class Route(db.Model):
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Campos atualizados
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    last_updated = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Novo campo para status de otimização
    is_optimized = db.Column(db.Boolean, default=False)
    optimized_at = db.Column(db.DateTime(timezone=True), nullable=True)
    optimization_status = db.Column(db.String(20), default='not_optimized')  # 'not_optimized', 'optimizing', 'optimized'
    
    # Novo campo para armazenar a geometria da rota OSRM
    route_geometry = db.Column(db.Text, nullable=True)  # Armazena a geometria codificada da rota OSRM
    route_duration = db.Column(db.Float, nullable=True)  # Duração em segundos
    route_distance = db.Column(db.Float, nullable=True)  # Distância em metros
    
    # Relação pai/filho para hierarquia geral de rotas
    parent_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=True)
    child_routes = db.relationship(
        'Route',
        backref=db.backref('parent_route', remote_side=[id]),
        foreign_keys=[parent_id]
    )
    
    # Relação para templates
    is_template = db.Column(db.Boolean, default=False)
    parent_template_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=True)
    template_instances = db.relationship(
        'Route',
        backref=db.backref('template_route', remote_side=[id]),
        foreign_keys=[parent_template_id]
    )
    
    # Relações
    company = db.relationship('Company', backref='routes')
    points = db.relationship('RoutePoint', backref='route', lazy=True, cascade='all, delete-orphan')
    
    # Rrelações
    locations = db.relationship(
        'Location',
        secondary='route_locations',
        viewonly=True 
    )
    
    route_locations = db.relationship(
        'RouteLocation',
        backref='route',
        cascade='all, delete-orphan'
    )

    @property
    def completed_points_count(self):
        """Retorna o número de pontos completados na rota."""
        return sum(1 for loc in self.route_locations if loc.check_in_at and loc.check_out_at)

    @property
    def total_points_count(self):
        """Retorna o número total de pontos na rota."""
        return len(self.route_locations)

    def mark_as_completed(self):
        """Marca a rota como concluída"""
        self.is_completed = True
        self.completed_at = datetime.now(timezone.utc)
    
    def mark_as_optimizing(self):
        """Marca a rota como em processo de otimização"""
        self.optimization_status = 'optimizing'
        db.session.commit()
    
    def mark_as_optimized(self):
        """Marca a rota como otimizada"""
        self.is_optimized = True
        self.optimized_at = datetime.now(timezone.utc)
        self.optimization_status = 'optimized'
        db.session.commit()
    
    def create_child_route(self):
        """Cria uma nova rota baseada nesta, como uma 'rota filha'"""
        child = Route(
            name=f"{self.name} (Nova)",
            description=self.description,
            creator_id=self.creator_id,
            company_id=self.company_id,
            parent_id=self.id
        )
        return child
        
    def get_avg_work_time(self):
        """Calcula o tempo médio de trabalho (entre check-in e check-out) para cada local visitado"""
        locations = [rl for rl in self.route_locations if rl.check_in_at and rl.check_out_at]
        if not locations:
            return 0
            
        total_minutes = sum(rl.get_work_time() or 0 for rl in locations)
        if len(locations) == 0:
            return 0
        return total_minutes / len(locations)
    
    def get_avg_transit_time(self):
        """Calcula o tempo médio de deslocamento entre locais visitados"""
        # Ordenar locais por ordem para calcular o tempo de trânsito corretamente
        locations = sorted([rl for rl in self.route_locations if rl.check_in_at], key=lambda x: x.order)
        
        if len(locations) <= 1:
            return 0
            
        transit_times = []
        for i in range(1, len(locations)):
            transit_time = locations[i].get_transit_time_from_previous(locations[i-1])
            if transit_time is not None:
                transit_times.append(transit_time)
                
        if not transit_times:
            return 0
        return sum(transit_times) / len(transit_times)
        
    def get_total_work_time(self):
        """Calcula o tempo total de trabalho em minutos."""
        total = 0
        for loc in self.route_locations:
            if loc.check_in_at and loc.check_out_at:
                total += loc.get_work_time()
        return round(total, 1)

    def get_avg_work_time(self):
        """Calcula o tempo médio de trabalho por local em minutos."""
        completed_locations = [loc for loc in self.route_locations 
                             if loc.check_in_at and loc.check_out_at]
        if not completed_locations:
            return 0
        total_time = sum(loc.get_work_time() for loc in completed_locations)
        return round(total_time / len(completed_locations), 1)
        
    def get_total_transit_time(self):
        """Calcula o tempo total de deslocamento entre todos os locais visitados"""
        locations = sorted([rl for rl in self.route_locations if rl.check_in_at], key=lambda x: x.order)
        
        if len(locations) <= 1:
            return 0
            
        total_minutes = 0
        for i in range(1, len(locations)):
            transit_time = locations[i].get_transit_time_from_previous(locations[i-1])
            if transit_time is not None:
                total_minutes += transit_time
                
        return total_minutes

    def is_assigned_to(self, user):
        """Verifica se um usuário está atribuído a esta rota"""
        if not user:
            return False
        return user in self.assigned_sellers

    def create_from_template(self, creator_id=None):
        """Creates a new route based on this template"""
        if not self.is_template:
            raise ValueError("Can only create routes from templates")
            
        creator_id = creator_id or (current_user.id if current_user else None)
        if not creator_id:
            raise ValueError("Creator ID is required")
            
        new_route = Route(
            name=f"{self.name} (Nova)",
            description=self.description,
            creator_id=creator_id,
            company_id=self.company_id,
            parent_template_id=self.id,
            is_template=False
        )
        return new_route

    @property
    def route_distance(self):
        """Retorna a distância total da rota em metros."""
        return getattr(self, '_route_distance', None)

    @route_distance.setter
    def route_distance(self, value):
        """Define a distância total da rota em metros."""
        self._route_distance = value

    def get_work_transit_ratio(self):
        """Calcula a proporção de tempo gasto em trabalho vs deslocamento"""
        total_work = self.get_total_work_time()
        total_transit = self.get_total_transit_time()
        
        total_time = total_work + total_transit
        if total_time == 0:
            return {'work_percent': 0, 'transit_percent': 0}
            
        work_percent = (total_work / total_time) * 100
        transit_percent = (total_transit / total_time) * 100
        
        return {
            'work_percent': round(work_percent, 1),
            'transit_percent': round(transit_percent, 1)
        }

class RoutePoint(db.Model):
    __tablename__ = 'route_points'
    
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    telephone = db.Column(db.String(20), nullable=True)
    order = db.Column(db.Integer, nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    is_visited = db.Column(db.Boolean, default=False)
    visited_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    def mark_as_visited(self):
        self.is_visited = True
        self.visited_at = datetime.now(timezone.utc)
        
    def mark_as_not_visited(self):
        self.is_visited = False
        self.visited_at = None

class RouteLocation(db.Model):
    """Modelo para gerenciar os locais de uma rota e seu status de visitação"""
    __tablename__ = 'route_locations'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    visited_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    visited_at = db.Column(db.DateTime(timezone=True), nullable=True) # Added nullable=True for consistency
    is_visited = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    # Novo campo: limiar de distância em metros para permitir marcação de visita
    distance_threshold = db.Column(db.Integer, default=100)  # Padrão: 100 metros
    
    # Campos para check-in e check-out
    check_in_at = db.Column(db.DateTime(timezone=True), nullable=True)
    check_out_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # Remova o atributo overlaps e backref para evitar conflitos
    # Relacionamentos
    location = db.relationship('Location', backref='route_locations')
    visited_by = db.relationship('User', foreign_keys=[visited_by_id])

    def __init__(self, route_id, location_id, order=0, distance_threshold=100):
        self.route_id = route_id
        self.location_id = location_id
        self.order = order
        self.is_visited = False
        self.distance_threshold = distance_threshold

    def __repr__(self):
        return f'<RouteLocation {self.route_id}-{self.location_id}>'
        
    def check_in(self, user_id):
        """Registra o check-in do usuário no local"""
        self.check_in_at = datetime.now(timezone.utc)
        self.visited_by_id = user_id
        db.session.commit()
        
    def check_out(self):
        """Registra o check-out do usuário no local"""
        self.check_out_at = datetime.now(timezone.utc)
        self.is_visited = True
        self.visited_at = self.check_out_at
        db.session.commit()
        
    def get_work_time(self):
        """Calcula o tempo de trabalho em minutos para este local."""
        if self.check_in_at and self.check_out_at:
            delta = self.check_out_at - self.check_in_at
            return round(delta.total_seconds() / 60, 1)
        return 0
    def get_transit_time_from_previous(self, previous_location):
        """Calcula o tempo de deslocamento do local anterior até este local em minutos"""
        if previous_location and previous_location.check_out_at and self.check_in_at:
            delta = self.check_in_at - previous_location.check_out_at
            return int(delta.total_seconds() / 60)
        return None

class Plan(db.Model):
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    is_free = db.Column(db.Boolean, default=False)
    duration_days = db.Column(db.Integer, nullable=True)  # NULL significa ilimitado
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Relacionamentos
    companies = db.relationship('Company', backref='plan', lazy=True)
