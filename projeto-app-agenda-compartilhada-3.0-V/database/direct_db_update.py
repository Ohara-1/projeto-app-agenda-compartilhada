import os
import sqlite3
import glob

def update_database():
    print("Iniciando atualização direta do banco de dados SQLite...")
    
    # Procurar pelo arquivo de banco de dados SQLite (normalmente em /instance)
    db_files = glob.glob('instance/*.sqlite') + glob.glob('*.sqlite')
    
    if not db_files:
        print("Nenhum banco de dados SQLite encontrado. Procurando em diretórios pais...")
        # Tentar diretórios pais
        parent_db_files = glob.glob('../instance/*.sqlite') + glob.glob('../*.sqlite')
        if not parent_db_files:
            print("Erro: Nenhum banco de dados SQLite encontrado.")
            return False
        db_files = parent_db_files
    
    db_path = db_files[0]
    print(f"Usando banco de dados: {db_path}")
    
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar se a tabela user existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("Erro: Tabela de usuários não encontrada.")
            return False
            
        # 2. Verificar se a coluna active_family_id já existe na tabela user
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'active_family_id' not in columns:
            print("Adicionando coluna active_family_id à tabela user...")
            # SQLite não tem bom suporte para ALTER TABLE, mas podemos adicionar colunas simples
            cursor.execute("ALTER TABLE user ADD COLUMN active_family_id INTEGER")
            
            # Definir active_family_id com o valor de family_id para todos os usuários
            if 'family_id' in columns:
                cursor.execute("UPDATE user SET active_family_id = family_id")
                print("Coluna active_family_id criada e preenchida com valores de family_id.")
            else:
                print("Coluna family_id não encontrada para migração.")
        else:
            print("Coluna active_family_id já existe.")
            
        # 3. Verificar se a tabela user_families existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_families'")
        if not cursor.fetchone():
            print("Criando tabela user_families...")
            cursor.execute("""
            CREATE TABLE user_families (
                user_id INTEGER NOT NULL, 
                family_id INTEGER NOT NULL, 
                PRIMARY KEY (user_id, family_id), 
                FOREIGN KEY(user_id) REFERENCES user (id), 
                FOREIGN KEY(family_id) REFERENCES family (id)
            )
            """)
            
            # Migrar dados: para cada usuário, adicionar sua família atual na tabela user_families
            if 'family_id' in columns:
                cursor.execute("""
                INSERT INTO user_families (user_id, family_id)
                SELECT id, family_id FROM user WHERE family_id IS NOT NULL
                """)
                print("Tabela user_families criada e dados migrados.")
            else:
                print("Coluna family_id não encontrada para migração.")
        else:
            print("Tabela user_families já existe.")
            
        # Commit das alterações
        conn.commit()
        print("Alterações no banco de dados confirmadas com sucesso!")
        
    except Exception as e:
        print(f"Erro ao atualizar o banco de dados: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    if update_database():
        print("Atualização do banco de dados concluída com sucesso!")
    else:
        print("Erro na atualização do banco de dados.") 