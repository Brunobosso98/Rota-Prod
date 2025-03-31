# Otimizador de Rotas Avançado

Sistema web completo para criação, otimização e gerenciamento de rotas de visita, projetado para equipes de vendas e logística. Inclui hierarquia de usuários, acompanhamento por geolocalização e estatísticas detalhadas.

## Funcionalidades Principais

- **Gestão de Usuários Hierárquica**:
  - **Administrador**: Gerencia toda a empresa, usuários (Gerentes, Vendedores), locais e rotas. Cria gerentes e vendedores. Atribui vendedores a gerentes.
  - **Gerente**: Gerencia os vendedores atribuídos a ele. Cria vendedores (automaticamente atribuídos a si). Cria e gerencia rotas para seus vendedores.
  - **Vendedor**: Visualiza e executa as rotas atribuídas. Realiza check-in/check-out nos locais.
- **Gestão de Locais**:
  - Cadastro manual de locais (clientes, pontos de entrega) com nome, endereço, coordenadas e telefone.
  - **Importação em Lote**: Importe locais facilmente a partir de arquivos **Excel (.xlsx, .xls)**.
  - Visualização e filtragem de locais por cidade/estado.
- **Criação e Atribuição de Rotas**:
  - Crie rotas selecionando múltiplos locais.
  - Defina um ponto de partida específico para a rota.
  - Atribua rotas a um ou mais vendedores.
- **Otimização de Rotas (TSP)**:
  - Algoritmo otimiza a sequência de visitas (Problema do Caixeiro Viajante) usando **OR-Tools**, respeitando o ponto de partida definido.
  - Integração com **OSRM** para obter o traçado real da rota no mapa, distância total e tempo estimado de percurso.
- **Execução e Acompanhamento**:
  - Visualização interativa da rota em mapa (Folium) com status dos pontos (partida, próximo, visitado, não visitado).
  - **Check-in/Check-out com Geofencing**: Vendedores realizam check-in e check-out nos locais. O sistema valida a proximidade usando a geolocalização do dispositivo contra um **limite de distância configurável**.
  - Registro de data/hora para check-in e check-out.
  - Marcação automática de ponto como visitado após check-out.
- **Gestão de Rotas Concluídas**:
  - Rotas são marcadas como concluídas automaticamente após o check-out no último ponto, ou manualmente.
  - Rotas concluídas são arquivadas e não podem ser alteradas.
- **Clonagem de Rotas**: Crie novas rotas rapidamente clonando rotas concluídas.
- **Templates de Rota**:
  - Salve rotas existentes como templates reutilizáveis (disponível para Admins e Gerentes).
  - Crie novas rotas a partir de templates salvos.
- **Estatísticas Detalhadas**:
  - **Por Rota**: Tempo médio e total de trabalho (check-in ao check-out) e deslocamento (entre check-out e check-in seguinte). Detalhes por local visitado.
  - **Por Vendedor**: Número total de rotas, rotas concluídas, taxa de conclusão, médias de tempo de trabalho e deslocamento.
- **Configurações do Sistema**:
  - Administrador pode definir o **limite de distância (metros)** para validação do check-in/check-out.

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- Dependências listadas em `requirements.txt`
- (Opcional, para otimização) Acesso a um servidor OSRM (público ou auto-hospedado) - configurado em `appReta.py`.

URL para super administrador mudar o plano do usuário:
http://localhost/admin/companies

## Instalação

1.  **Clone o repositório**:

    ```bash
    git clone <url-do-repositorio>
    cd rota
    ```

2.  **Crie e ative um ambiente virtual**:

    ```bash
    python -m venv venv
    # No Linux/macOS:
    source venv/bin/activate
    # No Windows:
    venv\Scripts\activate
    ```

3.  **Instale as dependências**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o Banco de Dados PostgreSQL**:

    - Crie um banco de dados (ex: `rota_dev`).
    - Configure as variáveis de ambiente ou crie um arquivo `.env` na raiz do projeto:

      ```ini
      FLASK_APP=run.py
      FLASK_ENV=development # ou production
      SECRET_KEY=sua_chave_secreta_aqui # Gere uma chave segura
      DATABASE_URL=postgresql://usuario:senha@host:porta/nome_db
      # Exemplo: DATABASE_URL=postgresql://postgres:admin@localhost:5432/rota_dev

      # Configurações de Email (Opcional, para recuperação de senha, etc.)
      MAIL_SERVER=smtp.example.com
      MAIL_PORT=587
      MAIL_USE_TLS=True
      MAIL_USERNAME=seu_email@example.com
      MAIL_PASSWORD=sua_senha
      MAIL_DEFAULT_SENDER=seu_email@example.com

      # Configuração OSRM (Opcional, para otimização de rotas)
      # OSRM_HOST=http://router.project-osrm.org # Exemplo: servidor público
      OSRM_HOST=http://localhost:5000 # Exemplo: servidor local
      ```

5.  **Inicialize e atualize o banco de dados**:

    - Certifique-se de que as variáveis de ambiente `FLASK_APP` e `DATABASE_URL` estão definidas.
    - Execute os comandos do Flask-Migrate:
      ```bash
      flask db init  # Apenas na primeira vez
      flask db migrate -m "Mensagem descritiva da migração" # Sempre que alterar os models
      flask db upgrade # Aplica as migrações ao banco
      ```
      _Nota: Se `flask db init` já foi executado, pule este comando._

6.  **Execute a aplicação**:
    ```bash
    flask run
    ```
    A aplicação estará disponível em `http://localhost:5000` (ou na porta configurada).

## Uso Básico

1.  **Registro Inicial**: Acesse a aplicação e registre o primeiro usuário **Administrador**, fornecendo dados da empresa (Nome, CNPJ) e do usuário (Nome, Email, Senha). Só pode haver um admin por CNPJ inicialmente.
2.  **Login**: Faça login com as credenciais criadas.
3.  **Gerenciar Usuários (Admin/Gerente)**: No menu lateral, acesse "Gerenciar Usuários" para criar Gerentes e Vendedores. Admins podem atribuir Vendedores a Gerentes.
4.  **Gerenciar Locais**: Adicione locais manualmente ou importe via Excel/PDF.
5.  **Criar Rota (Admin/Gerente)**: Vá em "Nova Rota", defina nome, descrição, selecione os locais, defina o ponto de partida e atribua vendedores.
6.  **Otimizar Rota**: Na visualização da rota, clique em "Otimizar Rota".
7.  **Executar Rota (Vendedor)**: Acesse a rota atribuída. Use os botões "Check-in" e "Check-out" nos locais. O sistema validará sua localização.
8.  **Visualizar Estatísticas**: Acesse as seções de estatísticas para acompanhar o desempenho.
9.  **Usar Templates**: Salve rotas como templates ou crie novas rotas a partir deles na seção "Templates".

## Estrutura do Arquivo Excel para Importação

O arquivo Excel deve conter as seguintes colunas (o nome pode variar ligeiramente, mas a ordem e o conteúdo são importantes):

| nome      | cidade         | estado | latitude | longitude | telefone (opcional) |
| :-------- | :------------- | :----- | :------- | :-------- | :------------------ |
| Cliente A | São Paulo      | SP     | -23.5505 | -46.6333  | (11) 99999-8888     |
| Cliente B | Rio de Janeiro | RJ     | -22.9068 | -43.1729  | 21 2222-3333        |
| ...       | ...            | ...    | ...      | ...       | ...                 |

- As colunas `nome`, `cidade`, `estado`, `latitude`, `longitude` são obrigatórias.
- A coluna `telefone` é opcional. O sistema tentará formatar o número.
- Linhas com dados inválidos ou faltantes (especialmente coordenadas) serão ignoradas.

## Tecnologias Utilizadas

- **Backend**: Python, Flask, SQLAlchemy (ORM), Flask-Login, Flask-Migrate, Flask-WTF, Werkzeug
- **Frontend**: HTML, CSS, JavaScript, Bootstrap, jQuery
- **Banco de Dados**: PostgreSQL
- **Mapeamento e Geocodificação**: Folium (visualização), Polyline (decodificação de geometria)
- **Otimização**: Google OR-Tools (TSP Solver)
- **Roteamento**: OSRM (Obtenção de traçado, distância, duração)
- **Manipulação de Dados**: Pandas (Importação Excel)

# Removed PDF manipulation from technologies

## Licença

Este projeto está licenciado sob a licença MIT.
