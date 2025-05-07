import os
import sys
from pathlib import Path

# Adicionar pasta raiz ao caminho de importação
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configurar variáveis de ambiente
os.environ['FLASK_APP'] = 'backend.__pycache__.backend.run'
os.environ['FLASK_ENV'] = 'development'

try:
    from backend.__pycache__.backend import create_app
    
    print("Iniciando a aplicação...")
    
    app = create_app()
    
    # Rode a aplicação
    app.run(debug=True)
    
except Exception as e:
    print(f"Erro ao iniciar a aplicação: {str(e)}")
    import traceback
    traceback.print_exc() 