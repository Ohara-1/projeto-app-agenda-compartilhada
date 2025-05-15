# Agenda Familiar Compartilhada

Um aplicativo web de agenda compartilhada para organização familiar, permitindo a gestão de eventos, tarefas e colaboração entre membros da família.

## Descrição

A Agenda Familiar Compartilhada é uma aplicação desenvolvida em Flask que permite que famílias organizem seus calendários, eventos e tarefas de forma colaborativa. Com esta aplicação, os usuários podem:

- Criar grupos familiares e convidar membros
- Gerenciar eventos no calendário compartilhado
- Criar e atribuir tarefas para membros da família
- Visualizar eventos próximos e tarefas pendentes
- Gerenciar permissões de administração no grupo familiar

## Tecnologias Utilizadas

- **Backend**: Python com Flask
- **Frontend**: HTML, CSS, JavaScript
- **Banco de Dados**: SQLite com SQLAlchemy
- **Autenticação**: Flask-Login
- **Formulários**: Flask-WTF
- **Comunicação em Tempo Real**: Flask-SocketIO

## Estrutura do Projeto

```
AgendaCompartilhada/
├── backend/               # Código do servidor Flask
│   ├── blueprints/        # Blueprints para organização de rotas
│   ├── forms/             # Formulários WTF
│   ├── models/            # Modelos de dados SQLAlchemy
│   ├── routes/            # Definições de rotas e controladores
│   ├── utils/             # Utilitários e helpers
│   ├── __init__.py        # Configuração da aplicação Flask
│   └── run.py             # Script de inicialização do servidor
├── database/              # Arquivos relacionados ao banco de dados
├── frontend/              # Código do cliente
│   ├── static/            # Arquivos estáticos (CSS, JS, imagens)
│   └── templates/         # Templates HTML Jinja2
│       ├── auth/          # Templates de autenticação
│       ├── calendar/      # Templates do calendário
│       ├── family/        # Templates de gerenciamento familiar
│       ├── layout/        # Templates de layout base
│       ├── tasks/         # Templates de tarefas
│       └── user/          # Templates de perfil de usuário
└── requirements.txt       # Dependências do projeto
```

## Principais Componentes

### Models (backend/models/)

- **User**: Gerencia usuários, autenticação e pertencimento a grupos
- **Family**: Representa um grupo familiar com seus membros e administradores
- **Event**: Eventos do calendário com data, hora e descrição
- **Task**: Tarefas que podem ser atribuídas a membros específicos

### Rotas (backend/routes/)

- Autenticação (login/registro/logout)
- Gestão de famílias (criação, convites, administração)
- Calendário (visualização, criação de eventos)
- Tarefas (gerenciamento, atribuição)
- Configurações e preferências de usuário

## Instalação e Configuração

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/AgendaCompartilhada.git
cd AgendaCompartilhada
```

2. Crie e ative um ambiente virtual:
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Execute a aplicação:
```
python backend/run.py
```

5. Acesse no navegador:
```
http://localhost:5000
```

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar pull requests ou abrir issues para melhorias e correções de bugs.

## Licença

Este projeto está licenciado sob a licença MIT.