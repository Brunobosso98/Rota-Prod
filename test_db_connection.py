import psycopg2

# Configurações do banco de dados
DB_HOST = '10.253.248.141'
DB_PORT = '5432'
DB_NAME = 'siterta'
DB_USER = 'rta'
DB_PASSWORD = 'rtapw'

def test_connection():
    try:
        # Tenta estabelecer a conexão
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        # Se chegou aqui, a conexão foi bem sucedida
        print("Conexão bem sucedida!")
        
        # Cria um cursor e testa uma query simples
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        print(f"Versão do PostgreSQL: {version[0]}")
        
        # Fecha o cursor e a conexão
        cur.close()
        conn.close()
        print("Conexão fechada com sucesso!")
        
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")

if __name__ == "__main__":
    test_connection()