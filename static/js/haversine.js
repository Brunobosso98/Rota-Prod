/**
 * Calcula a distância em metros entre dois pontos geográficos usando a fórmula de Haversine.
 * 
 * @param {Object} point1 - Objeto com latitude e longitude do primeiro ponto
 * @param {number} point1.latitude - Latitude do primeiro ponto em graus decimais
 * @param {number} point1.longitude - Longitude do primeiro ponto em graus decimais
 * @param {Object} point2 - Objeto com latitude e longitude do segundo ponto
 * @param {number} point2.latitude - Latitude do segundo ponto em graus decimais
 * @param {number} point2.longitude - Longitude do segundo ponto em graus decimais
 * @returns {number} Distância em metros entre os dois pontos
 */
function haversineDistance(point1, point2) {
    // Converter para números
    const lat1 = parseFloat(point1.latitude);
    const lon1 = parseFloat(point1.longitude);
    const lat2 = parseFloat(point2.latitude);
    const lon2 = parseFloat(point2.longitude);
    
    // Raio da Terra em metros
    const R = 6371000;
    
    // Converter graus para radianos
    const lat1Rad = lat1 * Math.PI / 180;
    const lon1Rad = lon1 * Math.PI / 180;
    const lat2Rad = lat2 * Math.PI / 180;
    const lon2Rad = lon2 * Math.PI / 180;
    
    // Diferença de latitude e longitude
    const dLat = lat2Rad - lat1Rad;
    const dLon = lon2Rad - lon1Rad;
    
    // Fórmula de Haversine
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1Rad) * Math.cos(lat2Rad) * 
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const distance = R * c;
    
    return distance;
} 