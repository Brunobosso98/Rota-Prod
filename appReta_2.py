from flask import Flask
import math
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import requests
import os
import polyline

app = Flask(__name__)

def haversine(lat1, lon1, lat2, lon2):
    """Calcula a distância (em km) entre dois pontos geográficos usando a fórmula de Haversine."""
    R = 6371  # Raio da Terra em km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def create_distance_matrix(points):
    """Pré-calcula a matriz de distâncias Haversine entre todos os pontos."""
    num_points = len(points)
    distance_matrix = [[0] * num_points for _ in range(num_points)]
    for i in range(num_points):
        for j in range(num_points):
            if i != j:
                # Calcula a distância e converte para metros inteiros, como esperado pelo OR-Tools
                distance_matrix[i][j] = int(haversine(
                    points[i][0], points[i][1],
                    points[j][0], points[j][1]
                ) * 1000)
    return distance_matrix

def solve_tsp_ortools(points, start_index=0, time_limit=120):
    """
    Resolve o TSP usando OR-Tools com matriz de distância pré-calculada.
    """
    if len(points) < 2:
        return list(range(len(points))) # Retorna a ordem original se houver 0 ou 1 ponto

    # 1. Pré-calcular a matriz de distâncias
    print(f"Pré-calculando a matriz de distâncias para {len(points)} pontos...")
    distance_matrix = create_distance_matrix(points)
    print("Matriz de distâncias calculada.")

    # 2. Configurar o Routing Manager e Model
    manager = pywrapcp.RoutingIndexManager(len(points), 1, start_index)
    routing = pywrapcp.RoutingModel(manager)

    # 3. Definir o callback de distância para LER da matriz pré-calculada
    def distance_callback(from_index, to_index):
        """Retorna a distância pré-calculada entre dois nós."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # Acessa diretamente a matriz pré-calculada
        return distance_matrix[from_node][to_node]

    # 4. Registrar o callback e definir o custo
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Configurações otimizadas
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.time_limit.seconds = time_limit
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.log_search = False

    solution = routing.SolveWithParameters(search_parameters)
    
    if solution:
        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))
        
        # Remove o último ponto se for igual ao primeiro (fecha o ciclo)
        if route[0] == route[-1]:
            route.pop()
            
        return route
    return None

def optimize_route(points, start_point=None):
    """
    Otimiza a rota usando OR-Tools com feedback sobre o status e aprimora
    com o OSRM para obter a geometria real das ruas.
    """
    try:
        print("\n" + "*" * 50)
        print("INICIANDO OTIMIZAÇÃO DE ROTA")
        
        if not points:
            print("ALERTA: Lista de pontos vazia!")
            return {'points': [], 'osrm_data': None}
        
        # Validação explícita do ponto de partida
        if start_point is None:
            print("ALERTA: Ponto de partida não fornecido!")
            if points:
                start_point = (float(points[0]['latitude']), float(points[0]['longitude']))
                print(f"Usando primeiro ponto como partida: {start_point}")
            else:
                return {'points': [], 'osrm_data': None}
        else:
            # Garantir que start_point seja uma tupla de floats
            try:
                start_lat, start_lon = start_point
                start_point = (float(start_lat), float(start_lon))
                print(f"Usando ponto de partida fornecido: {start_point}")
            except Exception as e:
                print(f"ERRO ao processar ponto de partida: {e}")
                return {'points': [], 'osrm_data': None}

        # INSPEÇÃO DETALHADA DO PONTO DE PARTIDA
        print(f"Ponto de partida recebido por optimize_route:")
        print(f"  Tipo: {type(start_point)}")
        print(f"  Valor: {start_point}")
        print(f"  ID de memória: {id(start_point)}")
        
        # CÓPIA EXPLÍCITA para evitar problemas de referência
        if start_point is not None:
            # Extrair valores e criar uma nova tupla para garantir que não haja problemas de referência
            start_lat, start_lon = start_point
            local_start_point = (float(start_lat), float(start_lon))
            print(f"Ponto de partida após cópia: {local_start_point}")
            print(f"ID de memória após cópia: {id(local_start_point)}")
        else:
            print("ERRO: start_point é None! Usando o primeiro ponto como partida")
            if points and len(points) > 0:
                local_start_point = (float(points[0]['latitude']), float(points[0]['longitude']))
                print(f"Usando coordenadas do primeiro ponto: {local_start_point}")
            else:
                print("ERRO FATAL: Não há pontos para usar como partida!")
                return {'points': [], 'osrm_data': None}
                
        # GARANTIR que o ponto de partida seja uma tupla de floats válida
        if not isinstance(local_start_point, tuple) or len(local_start_point) != 2:
            print(f"ERRO: Formato inválido do ponto de partida: {local_start_point}")
            return {'points': [], 'osrm_data': None}
        
        try:
            lat, lon = local_start_point
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                print(f"ERRO: Coordenadas do ponto de partida não são números: {local_start_point}")
                return {'points': [], 'osrm_data': None}
        except Exception as e:
            print(f"ERRO ao processar coordenadas: {e}")
            return {'points': [], 'osrm_data': None}
        
        print(f"Otimizando rota com {len(points)} pontos a partir de {local_start_point}")

        # Criar um ponto temporário para o ponto de partida
        start_point_dict = {'latitude': local_start_point[0], 'longitude': local_start_point[1], 'nome': 'Ponto de Partida', 'cidade': ''}
        print(f"Ponto de partida definido: {start_point_dict['latitude']}, {start_point_dict['longitude']}")

        if len(points) <= 1:
             print("Menos de 2 pontos de destino, retornando a ordem original.")
             # Tenta obter OSRM mesmo para 1 ponto (Partida -> Ponto 1)
             osrm_data = None
             if len(points) == 1:
                 try:
                     osrm_points = [start_point_dict] + points
                     osrm_data = get_osrm_route(osrm_points)
                 except Exception as e:
                     print(f"Erro ao obter OSRM para rota simples: {e}")
             return {'points': points, 'osrm_data': osrm_data}

        # --- MODIFICAÇÃO: Identificar ponto mais distante ---
        furthest_idx_orig = -1
        max_distance = -1
        print("\nCalculando ponto mais distante do ponto de partida...")
        for idx, point in enumerate(points):
            dist = haversine(
                local_start_point[0], local_start_point[1],
                point['latitude'], point['longitude']
            )
            print(f"  Distância partida -> {idx} ({point['nome']}): {dist:.2f} km")
            if dist > max_distance:
                max_distance = dist
                furthest_idx_orig = idx

        if furthest_idx_orig == -1:
            print("ERRO: Não foi possível identificar o ponto mais distante!")
            # Como fallback, não força nenhum ponto a ser o último
            furthest_point_data = None
            points_to_optimize = points # Otimiza todos
        else:
            furthest_point_data = points[furthest_idx_orig]
            print(f"Ponto mais distante identificado: Índice {furthest_idx_orig} ({furthest_point_data['nome']}), Distância: {max_distance:.2f} km")
            # Criar lista de pontos para otimizar (todos EXCETO o mais distante)
            points_to_optimize = [p for i, p in enumerate(points) if i != furthest_idx_orig]
            print(f"Total de pontos para otimização (excluindo o mais distante): {len(points_to_optimize)}")

        if not points_to_optimize:
            print("Não há pontos restantes para otimizar após remover o mais distante. Rota será apenas Partida -> Ponto Mais Distante.")
            optimized_points = [furthest_point_data] # A única parada é a mais distante
            osrm_data = None
            try:
                osrm_points = [start_point_dict] + optimized_points
                osrm_data = get_osrm_route(osrm_points)
            except Exception as e:
                print(f"Erro ao obter OSRM para rota Partida->Distante: {e}")
            return {'points': optimized_points, 'osrm_data': osrm_data}

        # Converter os pontos (sem o mais distante) para o formato de coordenadas do OR-Tools
        coords_to_optimize = [(p['latitude'], p['longitude']) for p in points_to_optimize]

        # Encontrar o ponto MAIS PRÓXIMO do ponto de partida DENTRO DA LISTA points_to_optimize
        closest_idx_subset = -1
        min_distance_subset = float('inf')
        print("\nEncontrando ponto mais próximo (no subconjunto) para iniciar a otimização...")
        for idx_subset, point_subset in enumerate(points_to_optimize):
            dist = haversine(
                local_start_point[0], local_start_point[1],
                point_subset['latitude'], point_subset['longitude']
            )
            print(f"  Distância partida -> Sub-Índice {idx_subset} ({point_subset['nome']}): {dist:.2f} km")
            if dist < min_distance_subset:
                min_distance_subset = dist
                closest_idx_subset = idx_subset # Índice dentro de coords_to_optimize

        if closest_idx_subset == -1:
            print("ERRO: Não foi possível encontrar o ponto mais próximo no subconjunto! Usando índice 0 do subconjunto.")
            closest_idx_subset = 0

        print(f"Ponto mais próximo no subconjunto é o Sub-Índice {closest_idx_subset} ({points_to_optimize[closest_idx_subset]['nome']}), distância: {min_distance_subset:.2f} km")

        # Resolver o TSP para o subconjunto de pontos
        print(f"\nChamando solve_tsp_ortools para {len(coords_to_optimize)} pontos, começando pelo Sub-Índice {closest_idx_subset}")
        sub_route_indices = solve_tsp_ortools(coords_to_optimize, start_index=closest_idx_subset, time_limit=120)

        if sub_route_indices:
            print(f"Ordem de visitação encontrada pelo OR-Tools (subconjunto): {sub_route_indices}")

            # Mapear os índices do subconjunto de volta para os pontos originais (sem o mais distante)
            intermediate_optimized_points = [points_to_optimize[i] for i in sub_route_indices]
            print(f"Primeiro ponto da rota otimizada (intermediária): {intermediate_optimized_points[0]['nome']}")

            # Construir a rota final: pontos intermediários otimizados + ponto mais distante no final
            if furthest_point_data:
                optimized_points = intermediate_optimized_points + [furthest_point_data]
                print(f"Ponto mais distante ({furthest_point_data['nome']}) adicionado ao final da rota.")
            else:
                 optimized_points = intermediate_optimized_points # Caso não tenha conseguido identificar o mais distante
                 print("AVISO: Ponto mais distante não identificado, rota final não o inclui no final.")

            print(f"\nRota final construída com {len(optimized_points)} pontos:")
            for i, p in enumerate(optimized_points):
                print(f"  {i+1}. {p['nome']}")

            # Calcula a distância total da rota final, considerando o ponto de partida
            total_distance = 0
            
            # Se o ponto de partida foi fornecido, calcule a distância até o primeiro ponto
            if local_start_point:
                dist_to_first = haversine(
                    local_start_point[0],
                    local_start_point[1],
                    optimized_points[0]['latitude'],
                    optimized_points[0]['longitude']
                )
                total_distance += dist_to_first
                print(f"Distância do ponto de partida ao primeiro ponto da rota: {dist_to_first:.2f} km")
            
            # Calcular distâncias entre pontos consecutivos da rota
            for i in range(len(optimized_points) - 1):
                segment_dist = haversine(
                    optimized_points[i]['latitude'],
                    optimized_points[i]['longitude'],
                    optimized_points[i + 1]['latitude'],
                    optimized_points[i + 1]['longitude']
                )
                total_distance += segment_dist
                print(f"Distância do ponto {i} ao ponto {i+1}: {segment_dist:.2f} km")
            
            print(f"Rota otimizada com sucesso! Distância total (haversine): {total_distance:.2f} km")
            
            # Tenta obter a rota real usando OSRM
            osrm_data = None
            try:
                # Para o OSRM, precisamos incluir o ponto de partida na rota
                if start_point_dict:
                    # Criar uma lista com o ponto de partida seguido pelos pontos otimizados
                    osrm_points = [start_point_dict] + optimized_points
                    
                    print(f"Enviando rota para OSRM com {len(osrm_points)} pontos (incluindo ponto de partida no início)")
                    print(f"Pontos para OSRM:")
                    print(f"  0. Partida: {osrm_points[0]['latitude']}, {osrm_points[0]['longitude']} (Ponto de Partida)")
                    for i, p in enumerate(osrm_points[1:], 1):
                        print(f"  {i}. {p['nome']}: {p['latitude']}, {p['longitude']}")
                    
                    osrm_data = get_osrm_route(osrm_points)
                else:
                    print("ALERTA: Ponto de partida não definido para OSRM!")
                    osrm_data = get_osrm_route(optimized_points)
                    
                if osrm_data and osrm_data['success']:
                    print(f"Rota OSRM obtida com sucesso! Distância: {osrm_data['distance']/1000:.2f} km, "
                          f"Tempo estimado: {osrm_data['duration']/60:.1f} min")
                    print(f"Geometria OSRM com {len(osrm_data['geometry'])} pontos")
                    if len(osrm_data['geometry']) > 0:
                        print(f"Primeiro ponto da geometria: {osrm_data['geometry'][0]}")
                else:
                    print(f"Erro ao obter rota OSRM: {osrm_data.get('error', 'Erro desconhecido') if osrm_data else 'Nenhuma resposta'}")
            except Exception as e:
                print(f"Erro ao processar rota OSRM: {str(e)}")
                # Continua com os pontos otimizados mesmo sem a geometria OSRM
            
            # O retorno deve incluir os pontos otimizados, mas não incluir o ponto de partida nessa lista
            print(f"Finalizando optimize_route com sucesso. Pontos otimizados: {len(optimized_points)}")
            print(f"Ponto de partida usado: {local_start_point}")
            print(f"Primeiro ponto da rota otimizada: {optimized_points[0]['nome']}")
            print(f"OSRM obtido: {'Sim' if osrm_data and osrm_data['success'] else 'Não'}")
            
            return {'points': optimized_points, 'osrm_data': osrm_data}
        
        print("Não foi possível encontrar uma solução otimizada com OR-Tools")
        fallback_points = fallback_nearest_neighbor(points, start_point)
        
        print(f"Usando algoritmo fallback: primeiro ponto da rota é {fallback_points[0]['nome']}")
        print(f"Ponto de partida usado no fallback: {local_start_point}")
        
        # Tenta obter a rota OSRM para o fallback também
        osrm_data = None
        try:
            if local_start_point:
                # Criar um ponto temporário para o ponto de partida
                start_point_dict = {'latitude': local_start_point[0], 'longitude': local_start_point[1], 'nome': 'Ponto de Partida', 'cidade': ''}
                # Adicionar ao início da lista para a chamada OSRM
                osrm_points = [start_point_dict] + fallback_points
                osrm_data = get_osrm_route(osrm_points)
            else:
                osrm_data = get_osrm_route(fallback_points)
        except Exception as e:
            print(f"Erro ao processar rota OSRM para fallback: {str(e)}")
            
        return {'points': fallback_points, 'osrm_data': osrm_data}
        
    except Exception as e:
        print(f"Erro no OR-Tools: {str(e)}")
        fallback_points = fallback_nearest_neighbor(points, start_point)
        
        # Tenta obter a rota OSRM para o fallback também
        osrm_data = None
        try:
            if local_start_point:
                # Criar um ponto temporário para o ponto de partida
                start_point_dict = {'latitude': local_start_point[0], 'longitude': local_start_point[1], 'nome': 'Ponto de Partida', 'cidade': ''}
                # Adicionar ao início da lista para a chamada OSRM
                osrm_points = [start_point_dict] + fallback_points
                osrm_data = get_osrm_route(osrm_points)
            else:
                osrm_data = get_osrm_route(fallback_points)
        except Exception as e:
            print(f"Erro ao processar rota OSRM para fallback: {str(e)}")
            
        return {'points': fallback_points, 'osrm_data': osrm_data}

def fallback_nearest_neighbor(points, start_point=None):
    """
    Implementa o algoritmo do vizinho mais próximo como fallback para o OR-Tools.
    Este é um algoritmo mais simples que encontra o ponto mais próximo do ponto atual
    e adiciona-o à rota iterativamente.
    
    Args:
        points (list): Lista de dicionários contendo os pontos (latitude, longitude, etc.)
        start_point (tuple): Ponto de partida (latitude, longitude), opcional
    
    Returns:
        list: Lista ordenada dos pontos
    """
    print("\nExecutando algoritmo de fallback (vizinho mais próximo)...")
    if not points:
        print("ERRO: Lista de pontos vazia!")
        return []
    
    # Validação do ponto de partida
    if start_point is None:
        print("AVISO: Ponto de partida não fornecido para fallback, usando o primeiro ponto.")
        if len(points) > 0:
            # Cria uma cópia para não modificar a lista original
            remaining_points = points.copy()
            current_point = remaining_points.pop(0)
            current_coords = (current_point['latitude'], current_point['longitude'])
            path = [current_point]
        else:
            return []
    else:
        # Garantir que start_point seja uma tupla de floats
        try:
            if isinstance(start_point, tuple) and len(start_point) == 2:
                start_lat, start_lon = start_point
                if isinstance(start_lat, (int, float)) and isinstance(start_lon, (int, float)):
                    current_coords = (float(start_lat), float(start_lon))
                    print(f"Usando ponto de partida: {current_coords}")
                else:
                    raise ValueError(f"Coordenadas inválidas: {start_point}")
            else:
                raise ValueError(f"Formato inválido para ponto de partida: {start_point}")
        except Exception as e:
            print(f"ERRO ao processar ponto de partida no fallback: {e}")
            # Usar o primeiro ponto como fallback do fallback
            if len(points) > 0:
                current_coords = (points[0]['latitude'], points[0]['longitude'])
            else:
                return []
                
        # Cria uma cópia da lista para não modificar o original
        remaining_points = points.copy()
        path = []
    
    print(f"Partindo de {current_coords}")
    print(f"Pontos restantes para processar: {len(remaining_points)}")
    
    # Continuar adicionando o ponto mais próximo iterativamente
    while remaining_points:
        closest_idx = 0
        closest_dist = float('inf')
        
        for idx, point in enumerate(remaining_points):
            dist = haversine(
                current_coords[0], current_coords[1],
                point['latitude'], point['longitude']
            )
            if dist < closest_dist:
                closest_dist = dist
                closest_idx = idx
        
        current_point = remaining_points.pop(closest_idx)
        path.append(current_point)
        current_coords = (current_point['latitude'], current_point['longitude'])
        
        if len(remaining_points) % 10 == 0 and len(remaining_points) > 0:
            print(f"Processados {len(path)} pontos, restam {len(remaining_points)}")
    
    print(f"Rota construída com {len(path)} pontos por vizinho mais próximo.")
    return path

def get_osrm_route(points):
    """
    Usa a API route do OSRM para calcular o trajeto real entre pontos já ordenados.
    
    Args:
        points (list): Lista de pontos ordenados no formato [{latitude, longitude}, ...]
        
    Returns:
        dict: Um dicionário contendo:
            - geometry (list): Lista de coordenadas [lat, lon] do trajeto
            - duration (float): Tempo total estimado em segundos
            - distance (float): Distância total em metros
            - success (bool): Se a requisição foi bem-sucedida
    """
    # Verificar se temos pontos suficientes
    if len(points) < 2:
        return {
            'success': False,
            'error': 'São necessários pelo menos 2 pontos para calcular uma rota'
        }
    
    # Obter a URL base do OSRM das variáveis de ambiente ou usar o serviço público
    osrm_base_url = os.environ.get('OSRM_URL', 'http://router.project-osrm.org')
    
    # Formatar as coordenadas como longitude,latitude para o OSRM
    # O OSRM espera coordenadas no formato "longitude,latitude", não "latitude,longitude"
    coordinates = ';'.join([f"{point['longitude']},{point['latitude']}" for point in points])
    
    # Montar a URL de requisição com parâmetros
    url = f"{osrm_base_url}/route/v1/driving/{coordinates}"
    params = {
        'overview': 'full',     # Obter geometria completa
        'annotations': 'true',  # Obter métricas detalhadas
        'steps': 'true',        # Obter instruções de navegação
        'geometries': 'geojson' # Formato de geometria mais fácil de trabalhar
    }
    
    try:
        # Fazer a requisição para o OSRM
        print(f"OSRM request: {url} with {len(points)} points")
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lançar exceção se status não for 200
        
        # Processar a resposta
        data = response.json()
        
        # Verificar se a resposta tem o formato esperado
        if data['code'] != 'Ok' or not data.get('routes'):
            return {
                'success': False,
                'error': data.get('message', 'Erro ao processar rota no OSRM')
            }
        
        # Obter a primeira rota (a mais otimizada)
        route = data['routes'][0]
        
        # Extrair a geometria (array de [lon, lat])
        geometry_coords = route['geometry']['coordinates']
        
        # Converter para formato [lat, lon] para manter consistência com o resto do código
        formatted_geometry = [[coord[1], coord[0]] for coord in geometry_coords]
        
        return {
            'success': True,
            'geometry': formatted_geometry,
            'duration': route['duration'],     # Em segundos
            'distance': route['distance'],     # Em metros
            'legs': route['legs'],             # Informações detalhadas por trecho
            'geometry_encoded': polyline.encode([(coord[0], coord[1]) for coord in formatted_geometry])
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição OSRM: {e}")
        return {
            'success': False,
            'error': f"Erro na requisição: {str(e)}"
        }
    except Exception as e:
        print(f"Erro ao processar resposta OSRM: {e}")
        return {
            'success': False,
            'error': f"Erro ao processar resposta: {str(e)}"
        }

if __name__ == "__main__":
    app.run(debug=True)
