import os
from dotenv import load_dotenv
from app import create_app
from waitress import serve

# Carrega variáveis de ambiente do arquivo .env se existir
load_dotenv()

# Cria a aplicação com a configuração especificada
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    # Em desenvolvimento, use Waitress
    if os.getenv('FLASK_ENV') == 'development':
        from waitress import serve
        print(f"Starting Waitress server on http://0.0.0.0:{os.getenv('PORT', 5000)}")
        serve(
            app,
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000))
        )
    else:
        # Em produção, o Gunicorn assume o controle
        app.run()