import math

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula a distância em metros entre dois pontos geográficos
    usando a fórmula de Haversine.
    
    Args:
        lat1: Latitude do primeiro ponto em graus decimais
        lon1: Longitude do primeiro ponto em graus decimais
        lat2: Latitude do segundo ponto em graus decimais
        lon2: Longitude do segundo ponto em graus decimais
        
    Returns:
        Distância em metros entre os dois pontos
    """
    # Raio da Terra em metros
    R = 6371000
    
    # Converter graus para radianos
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Diferença de latitude e longitude
    dLat = lat2_rad - lat1_rad
    dLon = lon2_rad - lon1_rad
    
    # Fórmula de Haversine
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * \
        math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance 
