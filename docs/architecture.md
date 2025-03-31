# Arquitetura do Sistema

## Visão Geral

O sistema utiliza uma arquitetura em camadas:

1. **Apresentação**

   - Flask (framework web)
   - Templates Jinja2
   - Bootstrap e jQuery

2. **Lógica de Negócios**

   - Módulos Python
   - OR-Tools para otimização
   - SQLAlchemy ORM

3. **Persistência**
   - PostgreSQL
   - Migrations Flask-Migrate

## Componentes Principais

### Otimizador de Rotas

- Algoritmo TSP (Problema do Caixeiro Viajante)
- K-means para clustering
- Integração com OSRM para rotas reais

### Sistema de Autenticação

- Flask-Login
- Hierarquia de usuários (Admin/Gerente/Vendedor)
- Tokens JWT para API

### Gestão de Dados

- Importação/Exportação Excel
- Cache com Redis

## Integrações

- OpenStreetMap/OSRM: Rotas e geocoding
- Serviços de email: Notificações
- APIs de clima: Previsão para rotas
