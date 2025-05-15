import pytest
from flask import url_for
from backend.models.models import User, Family

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_family(client, session):
    user = User(username="admin", email="admin@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    client.post(url_for('auth.login'), data={
        'email': 'admin@exemplo.com',
        'password': 'senha123'
    })
    
    response = client.post(url_for('main.create_family'), data={
        'name': 'Família Teste'
    })
    
    assert response.status_code == 302  # Redireciona após criação de família
    assert b'Grupo familiar criado com sucesso!' in response.data

def test_family_members(client, session):
    user = User(username="admin", email="admin@exemplo.com", password="senha123")
    family = Family(name="Família Teste", admin_id=user.id)
    session.add(user)
    session.add(family)
    session.commit()
    
    client.post(url_for('auth.login'), data={
        'email': 'admin@exemplo.com',
        'password': 'senha123'
    })
    
    response = client.get(url_for('main.family_members'))
    assert response.status_code == 200  # Acesso à página de membros da família
    assert b'Família Teste' in response.data  # Verifica se a família está na lista
