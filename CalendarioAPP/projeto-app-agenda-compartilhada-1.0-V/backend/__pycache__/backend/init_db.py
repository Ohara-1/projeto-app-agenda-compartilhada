from backend import db
from backend.models.models import User, Family, Event, Task
import os

print("Iniciando criação do banco de dados...")

# Criar todas as tabelas
db.create_all()

print("Tabelas criadas com sucesso!") 