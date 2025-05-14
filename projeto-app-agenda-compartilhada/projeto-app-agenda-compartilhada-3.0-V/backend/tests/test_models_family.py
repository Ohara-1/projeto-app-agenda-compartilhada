import pytest
from backend.models.models import Family, User

def test_create_family(session):
    user = User(username="admin", email="admin@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família Teste", admin_id=user.id)
    session.add(family)
    session.commit()
    
    assert family.id is not None
    assert family.name == "Família Teste"
    assert family.admin_id == user.id
