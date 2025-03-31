import requests

def geocodificar(endereco, api_key):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": endereco,
        "key": api_key,
        "region": "br"  # Foco em resultados brasileiros
    }
    response = requests.get(url, params=params).json()
    
    if response["status"] == "OK":
        lat = response["results"][0]["geometry"]["location"]["lat"]
        lng = response["results"][0]["geometry"]["location"]["lng"]
        return (lat, lng)
    else:
        return None

# Teste com diferentes formatos:
print(geocodificar("01311000", api_key))  # Só CEP
print(geocodificar("Avenida Paulista, 1000, São Paulo", api_key))  # Sem CEP
print(geocodificar("Praça da Sé, São Paulo, SP", api_key))  # Sem número