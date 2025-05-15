import pytest
from backend.models.models import Event, User, Family

def test_create_event(session):
    user = User(username="usuario_teste", email="teste@exemplo.com", password="senha123")
    family = Family(name="Família Teste", admin_id=user.id)
    session.add(user)
    session.add(family)
    session.commit()
    
    event = Event(title="Evento Teste", description="Descrição do evento", start_time="2023-10-01 10:00", end_time="2023-10-01 12:00", user_id=user.id, family_id=family.id)
    session.add(event)
    session.commit()
    
    assert event.id is not None
    assert event.title == "Evento Teste"
