# Documentação do Banco de Dados - Modelos (`models.py`)

Este documento descreve os modelos de banco de dados definidos em `models.py`.

## Modelos

### 1. Usuário (User)

- **Nome da Tabela:** `users`
- **Descrição:** Representa um usuário no sistema.
- **Colunas:**

  - `id` (Inteiro, Chave Primária): ID do usuário.
  - `username` (String(80), Único, Não Nulo): Nome de usuário para login.
  - `email` (String(120), Único, Não Nulo): Endereço de email do usuário.
  - `password_hash` (String(256)): Senha criptografada para autenticação.
  - `created_at` (DateTime, Padrão: `datetime.utcnow`): Data e hora de criação do usuário.
  - `name` (String(100), Nulável): Nome completo do usuário.
  - `role` (String(20), Não Nulo, Padrão: `'seller'`): Função do usuário (`'admin'`, `'manager'`, `'seller'`).
  - `company_id` (Inteiro, Chave Estrangeira: `companies.id`, Nulável): ID da empresa à qual o usuário pertence.

- **Relacionamentos:**

  - `routes` (Relacionamento): Um-para-muitos com modelo `Route` (usuário é o criador das rotas). Backref: `creator`.
  - `locations` (Relacionamento): Um-para-muitos com modelo `Location` (usuário é o criador dos locais). Backref: `creator`.
  - `managed_sellers` (Relacionamento): Muitos-para-muitos com o próprio modelo `User` (gerentes gerenciando vendedores). Tabela secundária: `manager_sellers`.
  - `managers` (Relacionamento, Backref de `managed_sellers`): Backref dinâmico para acessar gerentes de um vendedor.
  - `assigned_routes` (Relacionamento): Muitos-para-muitos com modelo `Route` (rotas atribuídas aos vendedores). Tabela secundária: `route_sellers`.
  - `company` (Relacionamento): Muitos-para-um com modelo `Company`. Backref: `users`.
  - `visited_by` (Relacionamento): Um-para-muitos com modelo `RouteLocation` (usuários que visitaram locais em rotas). Chave estrangeira: `visited_by_id` em `RouteLocation`.

- **Métodos:**
  - `display_name()`: Retorna o nome do usuário ou username se o nome não estiver definido.
  - `set_password(password)`: Define o hash da senha do usuário.
  - `check_password(password)`: Verifica se a senha fornecida corresponde ao hash da senha do usuário.
  - `is_admin()`: Retorna `True` se o usuário tem função `'admin'`.
  - `is_manager()`: Retorna `True` se o usuário tem função `'manager'`.
  - `is_seller()`: Retorna `True` se o usuário tem função `'seller'`.
  - `can_create_route()`: Retorna `True` se o usuário pode criar rotas (`'admin'` ou `'manager'`).
  - `get_total_work_time()`: Retorna o tempo total de trabalho em minutos.
  - `get_total_transit_time()`: Retorna o tempo total em trânsito em minutos.

---

### 2. Empresa (Company)

- **Nome da Tabela:** `companies`
- **Descrição:** Representa uma empresa no sistema.
- **Colunas:**

  - `id` (Inteiro, Chave Primária): ID da empresa.
  - `name` (String(100), Não Nulo): Nome da empresa.
  - `cnpj` (String(18), Único, Não Nulo): CNPJ da empresa.
  - `created_at` (DateTime, Padrão: `datetime.utcnow`): Data e hora de criação da empresa.

- **Relacionamentos:**
  - `users` (Relacionamento): Um-para-muitos com modelo `User`. Backref: `company`.
  - `locations` (Relacionamento): Um-para-muitos com modelo `Location`. Backref: `company`.
  - `routes` (Relacionamento): Um-para-muitos com modelo `Route`. Backref: `company`.

---

### 3. Local (Location)

- **Nome da Tabela:** `locations`
- **Descrição:** Representa um local geográfico.
- **Colunas:**

  - `id` (Inteiro, Chave Primária): ID do local.
  - `name` (String(100), Não Nulo): Nome do local.
  - `city` (String(100), Não Nulo): Cidade do local.
  - `state` (String(2), Não Nulo): Estado do local (ex: `'SP'`, `'RJ'`).
  - `latitude` (Float, Não Nulo): Latitude do local.
  - `longitude` (Float, Não Nulo): Longitude do local.
  - `telephone` (String(20), Nulável): Número de telefone do local (opcional).
  - `created_at` (DateTime, Padrão: `datetime.utcnow`): Data e hora de criação do local.
  - `creator_id` (Inteiro, Chave Estrangeira: `users.id`, Não Nulo): ID do usuário que criou o local.
  - `company_id` (Inteiro, Chave Estrangeira: `companies.id`, Não Nulo): ID da empresa à qual o local pertence.

- **Relacionamentos:**
  - `company` (Relacionamento): Muitos-para-um com modelo `Company`. Backref: `locations`.
  - `routes` (Relacionamento): Muitos-para-muitos com modelo `Route`. Tabela secundária: `route_locations`. Backref: `locations`.
  - `route_locations` (Relacionamento): Um-para-muitos com modelo `RouteLocation`. Backref: `location`.

---

### 4. Rota (Route)

- **Nome da Tabela:** `routes`
- **Descrição:** Representa uma rota composta por locais.
- **Colunas:**

  - `id` (Inteiro, Chave Primária): ID da rota.
  - `name` (String(100), Não Nulo): Nome da rota.
  - `created_at` (DateTime, Padrão: `datetime.utcnow`): Data e hora de criação da rota.
  - `creator_id` (Inteiro, Chave Estrangeira: `users.id`, Não Nulo): ID do usuário que criou a rota.
  - `company_id` (Inteiro, Chave Estrangeira: `companies.id`, Não Nulo): ID da empresa à qual a rota pertence.
  - `is_completed` (Boolean, Padrão: `False`): Indica se a rota foi completada.

- **Relacionamentos:**
  - `creator` (Relacionamento): Muitos-para-um com modelo `User`. Backref: `routes`.
  - `company` (Relacionamento): Muitos-para-um com modelo `Company`. Backref: `routes`.
  - `locations` (Relacionamento): Muitos-para-muitos com modelo `Location`. Tabela secundária: `route_locations`.
  - `sellers` (Relacionamento): Muitos-para-muitos com modelo `User`. Tabela secundária: `route_sellers`.
  - `route_locations` (Relacionamento): Um-para-muitos com modelo `RouteLocation`. Backref: `route`.

- **Métodos:**
  - `get_progress()`: Retorna o progresso da rota em porcentagem.
  - `get_visited_count()`: Retorna o número de locais visitados.
  - `get_points_count()`: Retorna o número total de pontos na rota.
  - `is_assigned_to(user)`: Verifica se a rota está atribuída a um usuário específico.
  - `get_total_work_time()`: Calcula o tempo total de trabalho na rota.
  - `get_total_transit_time()`: Calcula o tempo total em trânsito na rota.

---

### 5. RoutePoint

- **Table Name:** `route_points`
- **Description:** Represents a point within a route (deprecated, use `RouteLocation` instead).
- **Columns:**

  - `id` (Integer, Primary Key): RoutePoint ID.
  - `latitude` (Float, Not Nullable): Latitude of the point.
  - `longitude` (Float, Not Nullable): Longitude of the point.
  - `name` (String(100), Not Nullable): Name of the point.
  - `city` (String(100)): City of the point.
  - `state` (String(2)): State of the point.
  - `order` (Integer, Not Nullable): Order of the point in the route.
  - `route_id` (Integer, Foreign Key: `routes.id`, Not Nullable): ID of the route the point belongs to.
  - `location_id` (Integer, Foreign Key: `locations.id`, Nullable): ID of the location associated with the point (optional).
  - `created_at` (DateTime, Default: `datetime.utcnow`): Timestamp of route point creation.
  - `is_visited` (Boolean, Default: `False`): Indicates if the point is visited.
  - `visited_at` (DateTime, Nullable): Timestamp when the point was visited.

- **Relationships:**

  - `route` (Relationship): Many-to-one relationship with `Route` model. Backref: `points`.

- **Methods:**
  - `mark_as_visited()`: Marks the route point as visited and sets `visited_at` timestamp.
  - `mark_as_not_visited()`: Marks the route point as not visited and clears `visited_at` timestamp.

---

### 6. RouteLocation

- **Table Name:** `route_locations`
- **Description:** Manages locations within a route and their visit status.
- **Columns:**

  - `id` (Integer, Primary Key): RouteLocation ID.
  - `route_id` (Integer, Foreign Key: `routes.id`, Not Nullable): ID of the route.
  - `location_id` (Integer, Foreign Key: `locations.id`, Not Nullable): ID of the location.
  - `visited_by_id` (Integer, Foreign Key: `users.id`): ID of the user who visited the location.
  - `visited_at` (DateTime): Timestamp when the location was visited.
  - `is_visited` (Boolean, Default: `False`): Indicates if the location is visited in the route.
  - `order` (Integer, Default: `0`): Order of the location in the route.

- **Relationships:**
  - `route` (Relationship): Many-to-one relationship with `Route` model. Backref: `route_locations`.
  - `location` (Relationship): Many-to-one relationship with `Location` model. Backref: `route_locations`.
  - `visited_by` (Relationship): Many-to-one relationship with `User` model (user who visited the location).

---

### 7. Association Table: manager_sellers

- **Table Name:** `manager_sellers`
- **Description:** Association table for many-to-many relationship between managers and sellers (`User` model).
- **Columns:**
  - `manager_id` (Integer, Foreign Key: `users.id`, Primary Key): ID of the manager user.
  - `seller_id` (Integer, Foreign Key: `users.id`, Primary Key): ID of the seller user.

---

### 8. Association Table: route_sellers

- **Table Name:** `route_sellers`
- **Description:** Association table for many-to-many relationship between routes and sellers (`Route` and `User` models).
- **Columns:**
  - `route_id` (Integer, Foreign Key: `routes.id`, Primary Key): ID of the route.
  - `seller_id` (Integer, Foreign Key: `users.id`, Primary Key): ID of the seller user.

---

**Note:** This documentation is based on the models defined in `models.py`. It provides details on each model, their columns, relationships, and methods.
