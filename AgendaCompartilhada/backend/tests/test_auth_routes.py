import pytest
from flask import url_for
from backend.models.models import User

@pytest.fixture
def client(app):
    return app.test_client()

def test_login(client, session):
    # Criar um usuário para teste
    user = User(username="usuario_teste", email="teste@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    response = client.post(url_for('auth.login'), data={
        'email': 'teste@exemplo.com',
        'password': 'senha123'
    })
    
    assert response.status_code == 302  # Redireciona após login bem-sucedido
    assert b'Login falhou' not in response.data

def test_login_fail(client):
    response = client.post(url_for('auth.login'), data={
        'email': 'inexistente@exemplo.com',
        'password': 'senhaerrada'
    })
    
    assert response.status_code == 200  # Retorna a página de login
    assert b'Login falhou' in response.data

def test_register(client):
    response = client.post(url_for('auth.register'), data={
        'username': 'novo_usuario',
        'email': 'novo@exemplo.com',
        'password': 'senha123',
        'confirm_password': 'senha123'
    })
    
    assert response.status_code == 302  # Redireciona após registro bem-sucedido
    assert b'Conta criada com sucesso' in response.data

def test_register_fail(client):
    # Tentar registrar um usuário com email já existente
    user = User(username="usuario_teste", email="teste@exemplo.com", password="senha123")
    client.post(url_for('auth.register'), data={
        'username': 'usuario_teste',
        'email': 'teste@exemplo.com',
        'password': 'senha123',
        'confirm_password': 'senha123'
    })
    
    response = client.post(url_for('auth.register'), data={
        'username': 'usuario_teste2',
        'email': 'teste@exemplo.com',  # Email já existente
        'password': 'senha123',
        'confirm_password': 'senha123'
    })
    
    assert response.status_code == 200  # Retorna a página de registro
    assert b'Este email já está registrado' in response.data
