import pytest
from backend.models.models import Family, User

def test_create_family(session):
    # Teste básico de criação de família com admin
    user = User(username="admin", email="admin@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família Teste", admin_id=user.id)
    session.add(family)
    session.commit()
    
    assert family.id is not None
    assert family.name == "Família Teste"
    assert family.admin_id == user.id

def test_family_without_name(session):
    # Teste de validação: família não pode ser criada sem nome
    user = User(username="admin2", email="admin2@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    with pytest.raises(Exception):
        family = Family(name=None, admin_id=user.id)
        session.add(family)
        session.commit()

def test_family_without_admin(session):
    # Teste de validação: família não pode ser criada sem admin
    with pytest.raises(Exception):
        family = Family(name="Família Sem Admin", admin_id=None)
        session.add(family)
        session.commit()

def test_update_family(session):
    user = User(username="admin3", email="admin3@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Nome Original", admin_id=user.id)
    session.add(family)
    session.commit()
    
    # Teste de atualização do nome
    family.name = "Novo Nome"
    session.commit()
    
    updated_family = session.query(Family).filter_by(id=family.id).first()
    assert updated_family.name == "Novo Nome"

def test_delete_family(session):
    user = User(username="admin4", email="admin4@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família para Deletar", admin_id=user.id)
    session.add(family)
    session.commit()
    
    family_id = family.id
    session.delete(family)
    session.commit()
    
    # Verifica se a família foi realmente deletada
    deleted_family = session.query(Family).filter_by(id=family_id).first()
    assert deleted_family is None
