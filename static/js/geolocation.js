/**
 * Utilitários para gerenciar funcionalidades de geolocalização no navegador
 */
const GeoLocationUtils = {
    /**
     * Verifica se a geolocalização está disponível no navegador
     * @returns {boolean} true se disponível, false caso contrário
     */
    isGeolocationAvailable: function() {
        return 'geolocation' in navigator;
    },
    
    /**
     * Obtém a posição atual do usuário
     * @param {function} successCallback - Função chamada em caso de sucesso
     * @param {function} errorCallback - Função chamada em caso de erro
     * @param {object} options - Opções para a API de geolocalização
     */
    getCurrentPosition: function(successCallback, errorCallback, options = {}) {
        if (!this.isGeolocationAvailable()) {
            if (errorCallback) {
                errorCallback({
                    code: 0,
                    message: 'Geolocalização não disponível neste navegador'
                });
            }
            return;
        }
        
        const defaultOptions = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        };
        
        navigator.geolocation.getCurrentPosition(
            successCallback,
            errorCallback || function(error) {
                console.error('Erro ao obter localização:', error);
            },
            { ...defaultOptions, ...options }
        );
    },
    
    /**
     * Calcula a distância entre a posição do usuário e um ponto específico
     * @param {number} targetLat - Latitude do ponto alvo
     * @param {number} targetLon - Longitude do ponto alvo
     * @param {function} callback - Função chamada com a distância calculada
     */
    distanceToPoint: function(targetLat, targetLon, callback) {
        this.getCurrentPosition(
            function(position) {
                const userLat = position.coords.latitude;
                const userLon = position.coords.longitude;
                
                const distance = haversineDistance(
                    { latitude: userLat, longitude: userLon },
                    { latitude: targetLat, longitude: targetLon }
                );
                
                callback(distance);
            },
            function(error) {
                console.error('Erro ao calcular distância:', error);
                callback(null, error);
            }
        );
    },
    
    /**
     * Verifica se o usuário está próximo de um ponto específico
     * @param {number} targetLat - Latitude do ponto alvo
     * @param {number} targetLon - Longitude do ponto alvo
     * @param {number} thresholdMeters - Distância máxima em metros
     * @param {function} callback - Função chamada com o resultado
     */
    isNearPoint: function(targetLat, targetLon, thresholdMeters, callback) {
        this.distanceToPoint(targetLat, targetLon, function(distance, error) {
            if (error) {
                callback(false, error);
                return;
            }
            
            callback(distance <= thresholdMeters, null, distance);
        });
    },

    /**
     * Verifica a permissão atual da geolocalização
     * @returns {Promise} Promise com o status da permissão
     */
    checkGeolocationPermission: function() {
        return new Promise((resolve) => {
            if (!this.isGeolocationAvailable()) {
                resolve('not_available');
                return;
            }

            if (navigator.permissions && navigator.permissions.query) {
                navigator.permissions.query({ name: 'geolocation' })
                    .then(function(permissionStatus) {
                        resolve(permissionStatus.state); // 'granted', 'denied', 'prompt'
                    })
                    .catch(function() {
                        // Se não conseguir verificar permissão, assume que é 'prompt'
                        resolve('prompt');
                    });
            } else {
                // Navegadores antigos que não suportam a API Permissions
                resolve('prompt');
            }
        });
    },

    /**
     * Solicita permissão para acessar a geolocalização
     * @param {function} successCallback - Função chamada em caso de sucesso
     * @param {function} errorCallback - Função chamada em caso de erro
     */
    requestGeolocationPermission: function(successCallback, errorCallback) {
        if (!this.isGeolocationAvailable()) {
            if (errorCallback) {
                errorCallback({
                    code: 0,
                    message: 'Geolocalização não disponível neste navegador'
                });
            }
            return;
        }

        navigator.geolocation.getCurrentPosition(
            successCallback,
            errorCallback || function(error) {
                console.error('Erro ao solicitar permissão de geolocalização:', error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    },

    /**
     * Versão Promise do getCurrentPosition
     * @returns {Promise} Promise com a posição atual
     */
    getCurrentPosition: function() {
        return new Promise((resolve, reject) => {
            if (!this.isGeolocationAvailable()) {
                reject({
                    code: 0,
                    message: 'Geolocalização não disponível neste navegador'
                });
                return;
            }

            navigator.geolocation.getCurrentPosition(
                function(position) {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    });
                },
                function(error) {
                    reject(error);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        });
    }
}; 