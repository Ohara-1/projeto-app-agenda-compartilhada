import pytest
from backend.models.models import User

def test_create_user(session):
    user = User(username="usuario_teste", email="teste@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.email == "teste@exemplo.com"

def test_user_email_unique(session):
    user1 = User(username="usuario1", email="teste@exemplo.com", password="senha123")
    user2 = User(username="usuario2", email="teste@exemplo.com", password="senha456")
    
    session.add(user1)
    session.commit()
    
    with pytest.raises(Exception):
        session.add(user2)
        session.commit()

def test_user_password_hashing(session):
    user = User(username="usuario_teste", email="teste@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    assert user.password != "senha123"  # A senha deve ser armazenada como hash
