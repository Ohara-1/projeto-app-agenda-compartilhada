# Calendário Familiar

Um aplicativo de calendário compartilhado para famílias, com funcionalidades de login, registro de usuários, criação de grupos familiares, tarefas compartilhadas, avatares e chat.

## Tecnologias

- **Backend**: Python com Flask
- **Frontend**: HTML e CSS (sem JavaScript)
- **Banco de dados**: SQLite

## Funcionalidades

- Autenticação de usuários (login/registro)
- Criação e gerenciamento de grupos familiares
- Visualização de calendário compartilhado
- Criação e edição de eventos/tarefas
- Chat para comunicação entre membros da família
- Perfil de usuário com upload de avatar
- Convite de outros usuários para o grupo familiar

## Instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/calendario-familiar.git
cd calendario-familiar
```

2. Crie um ambiente virtual:
```
python -m venv venv
```

3. Ative o ambiente virtual:
   - Windows:
   ```
   venv\Scripts\activate
   ```
   - Linux/Mac:
   ```
   source venv/bin/activate
   ```

4. Instale as dependências:
```
pip install -r requirements.txt
```

5. Execute a aplicação:
```
python run.py
```

6. Abra o navegador e acesse:
```
http://127.0.0.1:5000
```

## Estrutura do Projeto

```
calendario/
│
├── app/
│   ├── __init__.py          # Inicialização da aplicação Flask
│   ├── models.py            # Modelos de dados
│   ├── forms.py             # Formulários
│   ├── routes.py            # Rotas da aplicação
│   │
│   ├── static/              # Arquivos estáticos
│   │   ├── css/
│   │   │   └── main.css     # Estilos da aplicação
│   │   │
│   │   └── avatars/         # Pasta para armazenar avatares
│   │       └── default.png  # Avatar padrão
│   │
│   └── templates/           # Templates HTML
│       ├── layout.html      # Template base
│       ├── login.html       # Página de login
│       ├── register.html    # Página de registro
│       ├── calendar.html    # Página do calendário
│       ├── chat.html        # Página do chat
│       ├── profile.html     # Página de perfil
│       ├── create_family.html # Criação de grupo familiar
│       ├── invite.html      # Página de convites
│       └── event_form.html  # Formulário de evento
│
├── run.py                 # Script para executar a aplicação
├── requirements.txt       # Dependências do projeto
└── README.md              # Documentação
```

## Notas

- É necessário criar um arquivo `.env` na raiz do projeto para definir a variável `SECRET_KEY` para maior segurança.
- A aplicação utiliza SQLite como banco de dados, portanto não é necessário configurar um servidor de banco de dados separado.
- Os avatares são armazenados na pasta `app/static/avatars/`.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests. 