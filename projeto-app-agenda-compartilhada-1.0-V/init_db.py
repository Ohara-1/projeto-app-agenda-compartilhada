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
    from backend.__pycache__.backend import create_app, db
    from backend.__pycache__.backend.models.models import User, Family
    from werkzeug.security import generate_password_hash
    
    print("Inicializando o banco de dados...")
    
    app = create_app()
    
    with app.app_context():
        # Criar as tabelas do banco de dados
        db.create_all()
        print("Tabelas criadas com sucesso!")
        
        # Criar um usuário de teste
        if not User.query.filter_by(email='teste@exemplo.com').first():
            print("Criando usuário de teste...")
            user = User(
                username='Usuário Teste',
                email='teste@exemplo.com',
                password=generate_password_hash('senha123')
            )
            db.session.add(user)
            db.session.commit()
            
            # Criar uma família para o usuário de teste
            print("Criando família de teste...")
            family = Family(
                name='Família Teste',
                admin_id=user.id
            )
            db.session.add(family)
            db.session.commit()
            
            # Adicionar o usuário à família e definir como ativa
            family.admins.append(user)
            user.families.append(family)
            user.active_family_id = family.id
            db.session.commit()
            
            print("Usuário e família de teste criados com sucesso!")
        
        print("Inicialização do banco de dados concluída com sucesso!")
    
except Exception as e:
    print(f"Erro ao inicializar o banco de dados: {str(e)}")
    import traceback
    traceback.print_exc() 