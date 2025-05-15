import pytest
from datetime import datetime, timedelta
from backend.models.models import Event, User, Family

def test_create_event(session):
    # Configuração básica de usuário e família
    user = User(username="usuario_teste", email="teste@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família Teste", admin_id=user.id)
    session.add(family)
    session.commit()
    
    # Criação do evento com datas como objetos datetime
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=2)
    
    event = Event(
        title="Evento Teste",
        description="Descrição do evento",
        start_time=start_time,
        end_time=end_time,
        user_id=user.id,
        family_id=family.id
    )
    session.add(event)
    session.commit()
    
    assert event.id is not None
    assert event.title == "Evento Teste"
    assert event.user_id == user.id
    assert event.family_id == family.id

def test_event_without_title(session):
    # Teste de validação: evento não pode ser criado sem título
    user = User(username="usuario2", email="teste2@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família Teste 2", admin_id=user.id)
    session.add(family)
    session.commit()
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=2)
    
    with pytest.raises(Exception):
        event = Event(
            title=None,
            description="Descrição do evento",
            start_time=start_time,
            end_time=end_time,
            user_id=user.id,
            family_id=family.id
        )
        session.add(event)
        session.commit()

def test_event_end_before_start(session):
    # Teste de validação: evento não pode terminar antes de começar
    user = User(username="usuario3", email="teste3@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família Teste 3", admin_id=user.id)
    session.add(family)
    session.commit()
    
    start_time = datetime.now()
    end_time = start_time - timedelta(hours=2)  # Data final antes da inicial
    
    with pytest.raises(Exception):
        event = Event(
            title="Evento Inválido",
            description="Evento com data final anterior à inicial",
            start_time=start_time,
            end_time=end_time,
            user_id=user.id,
            family_id=family.id
        )
        session.add(event)
        session.commit()

def test_update_event(session):
    user = User(username="usuario4", email="teste4@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família Teste 4", admin_id=user.id)
    session.add(family)
    session.commit()
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=2)
    
    event = Event(
        title="Evento Original",
        description="Descrição original",
        start_time=start_time,
        end_time=end_time,
        user_id=user.id,
        family_id=family.id
    )
    session.add(event)
    session.commit()
    
    # Atualização do evento
    new_start_time = start_time + timedelta(days=1)
    new_end_time = new_start_time + timedelta(hours=3)
    
    event.title = "Evento Atualizado"
    event.description = "Nova descrição"
    event.start_time = new_start_time
    event.end_time = new_end_time
    session.commit()
    
    updated_event = session.query(Event).filter_by(id=event.id).first()
    assert updated_event.title == "Evento Atualizado"
    assert updated_event.description == "Nova descrição"

def test_delete_event(session):
    user = User(username="usuario5", email="teste5@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família Teste 5", admin_id=user.id)
    session.add(family)
    session.commit()
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=2)
    
    event = Event(
        title="Evento para Deletar",
        description="Será deletado",
        start_time=start_time,
        end_time=end_time,
        user_id=user.id,
        family_id=family.id
    )
    session.add(event)
    session.commit()
    
    event_id = event.id
    session.delete(event)
    session.commit()
    
    # Verifica se o evento foi realmente deletado
    deleted_event = session.query(Event).filter_by(id=event_id).first()
    assert deleted_event is None
