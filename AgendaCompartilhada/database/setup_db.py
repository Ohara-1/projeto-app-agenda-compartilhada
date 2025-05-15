import os
import sqlite3

# Caminho para o banco de dados
DB_PATH = os.path.join('instance', 'db.sqlite')

# Garantir que o diretório instance exista
os.makedirs('instance', exist_ok=True)

# Criar conexão com o banco de dados
conn = sqlite3.connect(DB_PATH)

# Habilitar suporte a chaves estrangeiras
conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()

print(f"Criando banco de dados SQLite em: {DB_PATH}")

# Criar tabelas
print("Criando tabelas...")

# SQLite permite referências circulares desde que não sejam enforced imediatamente
# Precisamos desabilitar temporariamente o foreign key check quando criamos as tabelas
conn.execute("PRAGMA foreign_keys = OFF")

# Tabela user (primeiro sem a chave estrangeira)
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(150) NOT NULL,
    active_family_id INTEGER
)
''')

# Tabela family
cursor.execute('''
CREATE TABLE IF NOT EXISTS family (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    admin_id INTEGER NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES user (id)
)
''')

# Agora adicionamos a restrição à tabela user
cursor.execute('''
PRAGMA foreign_keys = ON;
''')

# Tabela user_families (relação many-to-many)
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_families (
    user_id INTEGER NOT NULL,
    family_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, family_id),
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (family_id) REFERENCES family (id)
)
''')

# Tabela family_admins (relação many-to-many)
cursor.execute('''
CREATE TABLE IF NOT EXISTS family_admins (
    family_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (family_id, user_id),
    FOREIGN KEY (family_id) REFERENCES family (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
)
''')

# Tabela event
cursor.execute('''
CREATE TABLE IF NOT EXISTS event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    family_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (family_id) REFERENCES family (id)
)
''')

# Tabela task
cursor.execute('''
CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(120) NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    completed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    family_id INTEGER NOT NULL,
    assigned_to_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (family_id) REFERENCES family (id),
    FOREIGN KEY (assigned_to_id) REFERENCES user (id)
)
''')

print("Tabelas criadas com sucesso!")

# Verificar se já existe usuário de teste
cursor.execute("SELECT COUNT(*) FROM user WHERE email = 'teste@exemplo.com'")
if cursor.fetchone()[0] == 0:
    print("Criando usuário de teste...")
    
    # Hash da senha 'senha123' (usando bcrypt - valor fixo para teste)
    hashed_password = 'pbkdf2:sha256:150000$nZyAO8Qc$0f6e27e99d6f7ab10ad88c9101bd517cc8e389e1ef50216bfde74a26d29e8452'
    
    # Inserir usuário
    cursor.execute('''
    INSERT INTO user (username, email, password)
    VALUES (?, ?, ?)
    ''', ('Usuário Teste', 'teste@exemplo.com', hashed_password))
    
    # Obter ID do usuário
    user_id = cursor.lastrowid
    
    # Inserir família
    cursor.execute('''
    INSERT INTO family (name, admin_id)
    VALUES (?, ?)
    ''', ('Família Teste', user_id))
    
    # Obter ID da família
    family_id = cursor.lastrowid
    
    # Atualizar usuário com família ativa
    cursor.execute('''
    UPDATE user SET active_family_id = ? WHERE id = ?
    ''', (family_id, user_id))
    
    # Adicionar usuário como membro da família
    cursor.execute('''
    INSERT INTO user_families (user_id, family_id)
    VALUES (?, ?)
    ''', (user_id, family_id))
    
    # Adicionar usuário como admin da família
    cursor.execute('''
    INSERT INTO family_admins (family_id, user_id)
    VALUES (?, ?)
    ''', (family_id, user_id))
    
    print("Usuário e família de teste criados com sucesso!")
else:
    print("Usuário de teste já existe.")

# Salvar alterações e fechar conexão
conn.commit()
conn.close()

print("Banco de dados inicializado com sucesso!") 