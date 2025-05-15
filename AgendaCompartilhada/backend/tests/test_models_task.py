import pytest
from backend.models.models import Task, User, Family

def test_create_task(session):
    user = User(username="usuario_teste", email="teste@exemplo.com", password="senha123")
    family = Family(name="Família Teste", admin_id=user.id)
    session.add(user)
    session.add(family)
    session.commit()
    
    task = Task(title="Tarefa Teste", description="Descrição da tarefa", due_date="2023-10-01", user_id=user.id, family_id=family.id)
    session.add(task)
    session.commit()
    
    assert task.id is not None
    assert task.title == "Tarefa Teste"
