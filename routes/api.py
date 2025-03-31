from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Route, RoutePoint, Location
from datetime import datetime
import pandas as pd
import os
import json
from werkzeug.utils import secure_filename
import hashlib
from sqlalchemy import or_, and_
from datetime import timezone

api = Blueprint('api', __name__)

@api.route('/routes', methods=['GET'])
@login_required
def get_routes():
    """Retorna todas as rotas do usuário atual"""
    routes = Route.query.filter_by(user_id=current_user.id).order_by(Route.created_at.desc()).all()
    
    result = []
    for route in routes:
        points_count = RoutePoint.query.filter_by(route_id=route.id).count()
        visited_count = RoutePoint.query.filter_by(route_id=route.id, is_visited=True).count()
        
        result.append({
            'id': route.id,
            'name': route.name,
            'created_at': route.created_at.strftime('%d/%m/%Y %H:%M'),
            'is_completed': route.is_completed,
            'points_count': points_count,
            'visited_count': visited_count,
            'progress': int((visited_count / points_count * 100) if points_count > 0 else 0)
        })
    
    return jsonify({'routes': result})

@api.route('/route/<int:route_id>/points', methods=['GET'])
@login_required
def get_route_points(route_id):
    """Retorna todos os pontos de uma rota específica"""
    # Verifica se a rota pertence ao usuário
    route = Route.query.filter_by(id=route_id, user_id=current_user.id).first_or_404()
    
    # Busca os pontos da rota ordenados
    points = RoutePoint.query.filter_by(route_id=route.id).order_by(RoutePoint.order).all()
    
    result = []
    for point in points:
        result.append({
            'id': point.id,
            'name': point.name,
            'city': point.city,
            'latitude': point.latitude,
            'longitude': point.longitude,
            'order': point.order,
            'is_visited': point.is_visited,
            'visited_at': point.visited_at.strftime('%d/%m/%Y %H:%M') if point.visited_at else None
        })
    
    return jsonify({
        'route': {
            'id': route.id,
            'name': route.name,
            'start_lat': route.start_lat,
            'start_lon': route.start_lon,
            'is_completed': route.is_completed
        },
        'points': result
    })

@api.route('/route/<int:route_id>/toggle_point/<int:point_id>', methods=['POST'])
@login_required
def toggle_point(route_id, point_id):
    """Alterna o status de visitado de um ponto"""
    # Verifica se a rota pertence ao usuário
    route = Route.query.filter_by(id=route_id, user_id=current_user.id).first_or_404()
    
    # Busca o ponto
    point = RoutePoint.query.filter_by(id=point_id, route_id=route_id).first_or_404()
    
    # Alterna o status de visitado
    if point.is_visited:
        point.mark_as_not_visited()
    else:
        point.mark_as_visited()
    
    # Verifica se todos os pontos foram visitados
    all_points = RoutePoint.query.filter_by(route_id=route_id).all()
    route.is_completed = all(p.is_visited for p in all_points)
    route.last_updated = datetime.now(timezone.utc)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_visited': point.is_visited,
        'visited_at': point.visited_at.strftime('%d/%m/%Y %H:%M') if point.visited_at else None,
        'route_completed': route.is_completed
    })

@api.route('/cities', methods=['GET'])
@login_required
def get_cities():
    """Retorna todas as cidades de um determinado estado ou todas se nenhum estado for fornecido"""
    state = request.args.get('state', '')
    
    # Configurar a consulta base de acordo com o papel do usuário
    if current_user.is_admin():
        # Admin vê todas as cidades da empresa
        base_query = db.session.query(Location.city).filter(
            Location.company_id == current_user.company_id
        )
    elif current_user.is_manager():
        # Gerente vê cidades da empresa
        base_query = db.session.query(Location.city).filter(
            Location.company_id == current_user.company_id
        )
    else:
        # Vendedor vê cidades de locais que criou
        base_query = db.session.query(Location.city).filter(
            Location.creator_id == current_user.id
        )
    
    # Aplicar filtro de estado se fornecido
    if state:
        query = base_query.filter(Location.state == state)
    else:
        query = base_query
    
    # Executar a consulta e obter cidades distintas
    cities = [city[0] for city in query.distinct().all()]
    return jsonify({'cities': sorted(cities)})

@api.route('/locations', methods=['GET'])
@login_required
def get_locations():
    """Retorna locais filtrados por estado e cidade"""
    state = request.args.get('state', '')
    city = request.args.get('city', '')
    
    # Construir filtros base
    filters = [Location.company_id == current_user.company_id]
    
    # Aplicar filtros de estado e cidade se fornecidos
    if state:
        filters.append(Location.state == state)
    if city:
        filters.append(Location.city == city)
    
    # Executar consulta com os filtros
    locations = Location.query.filter(*filters).order_by(Location.state, Location.city, Location.name).all()
    
    # Formatar resultado
    result = [{
        'id': loc.id,
        'name': loc.name,
        'city': loc.city,
        'state': loc.state,
        'latitude': loc.latitude,
        'longitude': loc.longitude
    } for loc in locations]
    
    return jsonify({'locations': result}) 