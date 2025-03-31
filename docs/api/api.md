# Documentação da API - Rotas Principais (`routes/api.py`)

## Endpoints

### 1. Estatísticas do Vendedor (`/seller_stats/<int:seller_id>`)

- **Endpoint:** `/seller_stats/<int:seller_id>`
- **Métodos:** `GET`
- **Descrição:** Retorna estatísticas detalhadas de um vendedor.
- **Autenticação:** Requer login do usuário (`@login_required`).
- **Parâmetros de URL:**
  - `seller_id` (Inteiro, Obrigatório): ID do vendedor.
- **Resposta (JSON):**
  ```json
  {
    "total_routes": 10,
    "completed_routes": 7,
    "active_routes": 3,
    "avg_work_time": 120.5,
    "avg_transit_time": 45.2,
    "completion_rate": 70.0
  }
  ```

### 2. Rotas do Vendedor (`/routes`)

- **Endpoint:** `/routes`
- **Métodos:** `GET`
- **Descrição:** Recupera todas as rotas do usuário atual.
  - **Autenticação:** Requer login do usuário (`@login_required`).
  - **Resposta (JSON):**
    ```json
    {
      "routes": [
        {
          "id": 1,
          "name": "Rota 1",
          "created_at": "18/03/2025 22:30",
          "is_completed": false,
          "points_count": 5,
          "visited_count": 2,
          "progress": 40
        },
        {
          "id": 2,
          "name": "Rota 2",
          "created_at": "15/03/2025 14:00",
          "is_completed": true,
          "points_count": 10,
          "visited_count": 10,
          "progress": 100
        }
      ]
    }
    ```
    - **Campos da Resposta:**
      - `id` (Inteiro): ID da rota.
      - `name` (String): Nome da rota.
      - `created_at` (String): Data e hora de criação da rota (formato `DD/MM/AAAA HH:MM`).
      - `is_completed` (Boolean): Indica se a rota está concluída.
      - `points_count` (Inteiro): Número total de pontos na rota.
      - `visited_count` (Inteiro): Número de pontos visitados na rota.
      - `progress` (Inteiro): Progresso de conclusão da rota em porcentagem.

### 3. Alternar Status de Visita do Ponto (`/route/<int:route_id>/toggle_point/<int:point_id>`)

- **Endpoint:** `/route/<int:route_id>/toggle_point/<int:point_id>`
- **Métodos:** `POST`
- **Descrição:** Alterna o status de visitado de um ponto específico em uma rota.
  - **Autenticação:** Requer login do usuário (`@login_required`).
  - **Parâmetros de Caminho:**
    - `route_id` (Inteiro, Obrigatório): ID da rota.
    - `point_id` (Inteiro, Obrigatório): ID do ponto.
  - **Autorização:**
    - Verifica se a rota pertence ao usuário atual. Retorna 404 se não encontrada ou não pertencer ao usuário.
  - **Resposta (JSON):**
    ```json
    {
      "success": true,
      "is_visited": true,
      "visited_at": "18/03/2025 22:35",
      "route_completed": false
    }
    ```
    - **Campos da Resposta:**
      - `success` (Boolean): Indica se a operação foi bem-sucedida.
      - `is_visited` (Boolean): Status atualizado de visitação do ponto.
      - `visited_at` (String, anulável): Data e hora atualizada da visita (formato `DD/MM/AAAA HH:MM`) ou `null` se marcado como não visitado.
      - `route_completed` (Boolean): Status atualizado de conclusão da rota após alternar o ponto.

### 4. Obter Cidades (`/cities`)

- **Endpoint:** `/cities`
- **Métodos:** `GET`
- **Descrição:** Recupera uma lista de cidades, opcionalmente filtrada por estado.
  - **Autenticação:** Requer login do usuário (`@login_required`).
  - **Parâmetros de Consulta:**
    - `state` (String, Opcional): Estado para filtrar as cidades. Se não fornecido, retorna cidades de todos os estados.
  - **Autorização:**
    - Funções Admin e Manager veem todas as cidades dentro de sua empresa.
    - Função Seller vê cidades das localizações que criou.
  - **Resposta (JSON):**
    ```json
    {
      "cities": ["São Paulo", "Rio de Janeiro", "Belo Horizonte"]
    }
    ```
    - **Campos da Resposta:**
      - `cities` (Array de Strings): Lista ordenada de nomes únicos de cidades.

### 5. Obter Localizações (`/locations`)

- **Endpoint:** `/locations`
- **Métodos:** `GET`
- **Descrição:** Recupera localizações, filtradas por estado e cidade.
  - **Autenticação:** Requer login do usuário (`@login_required`).
  - **Parâmetros de Consulta:**
    - `state` (String, Opcional): Estado para filtrar localizações.
    - `city` (String, Opcional): Cidade para filtrar localizações.
  - **Autorização:**
    - Retorna localizações dentro da empresa do usuário atual.
  - **Resposta (JSON):**
    ```json
    {
      "locations": [
        {
          "id": 1,
          "name": "Localização A",
          "city": "São Paulo",
          "state": "SP",
          "latitude": -23.55,
          "longitude": -46.63
        },
        {
          "id": 2,
          "name": "Localização B",
          "city": "Rio de Janeiro",
          "state": "RJ",
          "latitude": -22.9068,
          "longitude": -43.1729
        }
      ]
    }
    ```
    - **Campos da Resposta:**
      - `locations` (Array de Objetos): Lista de localizações.
        - `id` (Inteiro): ID da localização.
        - `name` (String): Nome da localização.
        - `city` (String): Cidade da localização.
        - `state` (String): Estado da localização.
        - `latitude` (Float): Latitude da localização.
        - `longitude` (Float): Longitude da localização.

---

**Nota:** Esta documentação é baseada nas rotas definidas em `routes/api.py`. Ela fornece detalhes sobre cada rota, seus métodos, descrições, parâmetros, formatos de requisição e formatos de resposta.
