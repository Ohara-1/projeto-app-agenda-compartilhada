import pytest
from flask import url_for
from backend.models.models import User, Family, Event

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_event(client, session):
    user = User(username="usuario_teste", email="teste@exemplo.com", password="senha123")
    family = Family(name="Família Teste", admin_id=user.id)
    session.add(user)
    session.add(family)
    session.commit()
    
    client.post(url_for('auth.login'), data={
        'email': 'teste@exemplo.com',
        'password': 'senha123'
    })
    
    response = client.post(url_for('main.new_event'), data={
        'title': 'Evento Teste',
        'description': 'Descrição do evento',
        'start_time': '2023-10-01 10:00',
        'end_time': '2023-10-01 12:00'
    })
    
    assert response.status_code == 302  # Redireciona após criação de evento
    assert b'Evento criado com sucesso' in response.data

def test_event_list(client, session):
    user = User(username="usuario_teste", email="teste@exemplo.com", password="senha123")
    family = Family(name="Família Teste", admin_id=user.id)
    session.add(user)
    session.add(family)
    session.commit()
    
    event = Event(title="Evento Teste", description="Descrição do evento", start_time="2023-10-01 10:00", end_time="2023-10-01 12:00", user_id=user.id, family_id=family.id)
    session.add(event)
    session.commit()
    
    client.post(url_for('auth.login'), data={
        'email': 'teste@exemplo.com',
        'password': 'senha123'
    })
    
    response = client.get(url_for('main.events'))
    assert response.status_code == 200  # Acesso à página de eventos
    assert b'Evento Teste' in response.data  # Verifica se o evento está na lista
