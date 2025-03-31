import os
import psycopg2
from urllib.parse import urlparse

# Pegar a URL do banco das variáveis de ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')

def test_connection():
    try:
        # Parsear a URL do banco
        url = urlparse(DATABASE_URL)
        
        # Conectar usando os componentes da URL
        conn = psycopg2.connect(
            dbname=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        
        print("Conexão bem sucedida!")
        
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        print(f"Versão do PostgreSQL: {version[0]}")
        
        cur.close()
        conn.close()
        print("Conexão fechada com sucesso!")
        
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")

if __name__ == '__main__':
    test_connection()
