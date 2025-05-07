import os
import sys
import sqlite3
from pathlib import Path

# Adicionar pasta raiz ao caminho de importação
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from backend.__pycache__.backend import create_app, db
from flask import current_app

def update_database():
    print("Iniciando atualização do banco de dados...")
    
    # Obter o caminho do banco de dados
    with create_app().app_context():
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        print(f"Caminho do banco de dados: {db_path}")
    
    # Conectar ao banco de dados SQLite diretamente
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna active_family_id já existe
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'active_family_id' not in columns:
            print("Adicionando coluna active_family_id à tabela user...")
            # Adicionar a coluna active_family_id
            cursor.execute("ALTER TABLE user ADD COLUMN active_family_id INTEGER REFERENCES family(id)")
            
            # Atualizar os valores de active_family_id com os valores existentes de family_id
            cursor.execute("UPDATE user SET active_family_id = family_id")
            
            print("Coluna active_family_id adicionada.")
        else:
            print("Coluna active_family_id já existe.")
        
        # Verificar se a tabela user_families existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_families'")
        if not cursor.fetchone():
            print("Criando tabela user_families...")
            # Criar a tabela user_families
            cursor.execute("""
            CREATE TABLE user_families (
                user_id INTEGER NOT NULL, 
                family_id INTEGER NOT NULL, 
                PRIMARY KEY (user_id, family_id), 
                FOREIGN KEY(user_id) REFERENCES user (id), 
                FOREIGN KEY(family_id) REFERENCES family (id)
            )
            """)
            
            # Migrar dados existentes - adicionar registros na tabela user_families
            # baseados na relação família atual de cada usuário
            cursor.execute("INSERT INTO user_families SELECT id, family_id FROM user WHERE family_id IS NOT NULL")
            
            print("Tabela user_families criada e dados migrados.")
        else:
            print("Tabela user_families já existe.")
        
        # Commit das alterações
        conn.commit()
        print("Alterações no banco de dados confirmadas.")
        
    except Exception as e:
        print(f"Erro ao atualizar o banco de dados: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    if update_database():
        print("Atualização do banco de dados concluída com sucesso!")
    else:
        print("Erro na atualização do banco de dados.") 