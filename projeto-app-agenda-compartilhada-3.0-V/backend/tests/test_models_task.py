import pytest
from datetime import datetime, timedelta
from backend.models.models import Task, User, Family

def test_create_task(session):
    # Primeiro criamos o usuário
    user = User(username="usuario_teste", email="teste@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    # Depois criamos a família com o ID do usuário
    family = Family(name="Família Teste", admin_id=user.id)
    session.add(family)
    session.commit()
    
    # Por fim criamos a tarefa
    due_date = datetime.now() + timedelta(days=1)
    task = Task(
        title="Tarefa Teste",
        description="Descrição da tarefa",
        due_date=due_date,
        user_id=user.id,
        family_id=family.id
    )
    session.add(task)
    session.commit()
    
    assert task.id is not None
    assert task.title == "Tarefa Teste"
    assert task.user_id == user.id
    assert task.family_id == family.id

def test_task_without_title(session):
    # Configuração inicial
    user = User(username="usuario_teste2", email="teste2@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família Teste 2", admin_id=user.id)
    session.add(family)
    session.commit()
    
    # Teste de criação de tarefa sem título
    due_date = datetime.now() + timedelta(days=1)
    with pytest.raises(Exception):
        task = Task(
            title=None,
            description="Descrição da tarefa",
            due_date=due_date,
            user_id=user.id,
            family_id=family.id
        )
        session.add(task)
        session.commit()

def test_task_update(session):
    # Configuração inicial
    user = User(username="usuario_teste3", email="teste3@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família Teste 3", admin_id=user.id)
    session.add(family)
    session.commit()
    
    # Criação da tarefa
    due_date = datetime.now() + timedelta(days=1)
    task = Task(
        title="Tarefa Original",
        description="Descrição original",
        due_date=due_date,
        user_id=user.id,
        family_id=family.id
    )
    session.add(task)
    session.commit()
    
    # Atualização da tarefa
    task.title = "Tarefa Atualizada"
    task.description = "Nova descrição"
    new_due_date = datetime.now() + timedelta(days=2)
    task.due_date = new_due_date
    session.commit()
    
    # Verificação da atualização
    updated_task = session.query(Task).filter_by(id=task.id).first()
    assert updated_task.title == "Tarefa Atualizada"
    assert updated_task.description == "Nova descrição"

def test_task_delete(session):
    # Configuração inicial
    user = User(username="usuario_teste4", email="teste4@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família Teste 4", admin_id=user.id)
    session.add(family)
    session.commit()
    
    # Criação da tarefa
    due_date = datetime.now() + timedelta(days=1)
    task = Task(
        title="Tarefa para Deletar",
        description="Será deletada",
        due_date=due_date,
        user_id=user.id,
        family_id=family.id
    )
    session.add(task)
    session.commit()
    
    # Deletar a tarefa
    task_id = task.id
    session.delete(task)
    session.commit()
    
    # Verificar se foi deletada
    deleted_task = session.query(Task).filter_by(id=task_id).first()
    assert deleted_task is None

def test_task_with_invalid_date(session):
    # Configuração inicial
    user = User(username="usuario_teste5", email="teste5@exemplo.com", password="senha123")
    session.add(user)
    session.commit()
    
    family = Family(name="Família Teste 5", admin_id=user.id)
    session.add(family)
    session.commit()
    
    # Teste com data inválida
    with pytest.raises(Exception):
        task = Task(
            title="Tarefa Teste",
            description="Descrição da tarefa",
            due_date="data-invalida",
            user_id=user.id,
            family_id=family.id
        )
        session.add(task)
        session.commit()
