from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory, current_app
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
import calendar as cal_module
import os
from backend import db
from backend.models.models import User, Family, Event, Task
from backend.forms.forms import LoginForm, RegistrationForm, FamilyForm, EventForm, ProfileForm, TaskForm

main = Blueprint('main', __name__)

# Rota para selecionar a família ativa
@main.route('/select_family/<int:family_id>')
@login_required
def select_family(family_id):
    family = Family.query.get_or_404(family_id)
    
    # Verificar se o usuário pertence à família
    if current_user not in family.members:
        flash('Você não pertence a esta família.', 'error')
        return redirect(url_for('main.family_options'))
    
    current_user.active_family_id = family_id
    db.session.commit()
    
    # Limpar eventos antigos automaticamente ao selecionar uma família
    clean_count = clean_past_events(family_id)
    if clean_count > 0:
        flash(f'Alterado para o calendário: {family.name}', 'success')
        flash(f'{clean_count} eventos antigos foram automaticamente removidos.', 'info')
    else:
        flash(f'Alterado para o calendário: {family.name}', 'success')
    
    return redirect(url_for('main.calendar'))

# Função para limpar eventos antigos
def clean_past_events(family_id):
    """
    Remove eventos que já passaram da data de término.
    Retorna a quantidade de eventos removidos.
    """
    now = datetime.now()
    past_events = Event.query.filter_by(family_id=family_id).filter(Event.end_time < now).all()
    count = len(past_events)
    
    for event in past_events:
        db.session.delete(event)
    
    if count > 0:
        db.session.commit()
        
    return count

# Rotas de autenticação
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.calendar'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.calendar'))
        else:
            flash('Login falhou. Verifique seu email e senha.', 'error')
    return render_template('auth/login.html', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.calendar'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Sua conta foi criada com sucesso! Agora você precisa fazer login para acessar o sistema.', 'success')
        return redirect(url_for('main.login'))
    return render_template('auth/register.html', form=form)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        # Validação básica
        if not username or not email:
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(url_for('main.profile'))
        
        # Verificar se o email já está sendo usado (se for diferente do email atual do usuário)
        if email != current_user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Este email já está em uso por outro usuário.', 'error')
                return redirect(url_for('main.profile'))
        
        # Atualizar os dados do usuário
        current_user.username = username
        current_user.email = email
        db.session.commit()
        
        flash('Perfil atualizado com sucesso!', 'success')
    
    return render_template('user/profile.html')

# Rotas da família
@main.route('/create_family', methods=['GET', 'POST'])
@login_required
def create_family():
    form = FamilyForm()
    if form.validate_on_submit():
        try:
            family = Family(
                name=form.name.data,
                admin_id=current_user.id
            )
            db.session.add(family)
            db.session.commit()
            
            family.admins.append(current_user)
            # Adicionar usuário à família
            current_user.families.append(family)
            # Definir como família ativa
            current_user.active_family_id = family.id
            db.session.commit()
            
            flash('Grupo familiar criado com sucesso!', 'success')
            return redirect(url_for('main.calendar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar família: {str(e)}', 'error')
            return render_template('family/create_family.html', form=form)
            
    return render_template('family/create_family.html', form=form)

@main.route('/join_family/<token>')
@login_required
def join_family(token):
    family = Family.verify_join_token(token)
    if not family:
        flash('Link inválido ou expirado!', 'error')
        return redirect(url_for('main.calendar'))
    
    # Verificar se o usuário já pertence a esta família
    if current_user.families.filter_by(id=family.id).first():
        flash(f'Você já pertence ao grupo familiar {family.name}.', 'info')
        return redirect(url_for('main.calendar'))
    
    # Adicionar usuário à família
    current_user.families.append(family)
    # Definir como família ativa se não tiver uma
    if not current_user.active_family_id:
        current_user.active_family_id = family.id
    db.session.commit()
    
    flash(f'Você entrou no grupo familiar {family.name}!', 'success')
    return redirect(url_for('main.calendar'))

@main.route('/invite')
@login_required
def invite():
    if not current_user.active_family or current_user not in current_user.active_family.admins:
        flash('Você precisa ser o administrador de um grupo familiar para convidar pessoas.', 'error')
        return redirect(url_for('main.calendar'))
    
    token = current_user.active_family.get_join_token()
    invite_link = url_for('main.join_family', token=token, _external=True)
    return render_template('family/invite.html', invite_link=invite_link)

@main.route('/join_family', methods=['GET', 'POST'])
@login_required
def join_family_page():
    if request.method == 'POST':
        invite_link = request.form.get('invite_link')
        # Extrai o token do link (assume que termina com /join_family/<token>)
        import re
        match = re.search(r'/join_family/([\w\-\.]+)', invite_link)
        if match:
            token = match.group(1)
            return redirect(url_for('main.join_family', token=token))
        else:
            flash('Link de convite inválido!', 'error')
    return render_template('family/join_family.html')

# Rotas do calendário
@main.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.active_family_id:
            return redirect(url_for('main.calendar'))
        else:
            return redirect(url_for('main.family_options'))
    else:
        return redirect(url_for('main.login'))

@main.route('/calendar')
@login_required
def calendar():
    # Obter mês e ano da URL ou usar o atual
    today = date.today()
    year = request.args.get('year', type=int, default=today.year)
    month = request.args.get('month', type=int, default=today.month)
    
    # Validar mês e ano
    if month < 1 or month > 12:
        month = today.month
    if year < 2000 or year > 2100:  # Limites arbitrários
        year = today.year
    
    # Variáveis básicas para qualquer cenário
    first_day_of_month = cal_module.monthrange(year, month)[0]
    days_in_month = cal_module.monthrange(year, month)[1]
    
    if not current_user.active_family_id:
        # Redirecionar para a página de gerenciar grupos em vez de mostrar calendário vazio
        return redirect(url_for('main.family_options'))
    
    # Limpar eventos antigos
    removed_count = clean_past_events(current_user.active_family_id)
    if removed_count > 0:
        flash(f'{removed_count} eventos antigos foram automaticamente removidos.', 'info')
    
    # Buscar todos os eventos do mês selecionado para a família ativa do usuário
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    events = Event.query.filter_by(family_id=current_user.active_family_id).all()
    
    # Buscar todas as tarefas da família
    tasks = Task.query.filter_by(family_id=current_user.active_family_id, completed=False).all()
    
    # Filtrar eventos futuros para a seção de próximos eventos
    upcoming_events = [event for event in events if event.start_time >= datetime.now()]
    upcoming_events.sort(key=lambda x: x.start_time)
    upcoming_events = upcoming_events[:5]
    
    # Tarefas pendentes
    pending_tasks = Task.query.filter_by(family_id=current_user.active_family_id, completed=False).order_by(Task.due_date.asc()).limit(5).all()
    
    return render_template('calendar/calendar.html', 
                          events=events, 
                          tasks=tasks,
                          upcoming_events=upcoming_events,
                          pending_tasks=pending_tasks,
                          days_in_month=days_in_month,
                          first_day_of_month=first_day_of_month,
                          current_year=year,
                          current_month=month,
                          today=today)

@main.route('/event/new', methods=['GET', 'POST'])
@login_required
def new_event():
    if not current_user.active_family_id:
        return redirect(url_for('main.family_options'))
    
    form = EventForm()
    if form.validate_on_submit():
        print(f"Validação passou! Título: {form.title.data}")
        print(f"Start time: {form.start_time.data}")
        print(f"End time: {form.end_time.data}")
        event = Event(
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            user_id=current_user.id,
            family_id=current_user.active_family_id
        )
        db.session.add(event)
        db.session.commit()
        flash('Evento criado com sucesso!', 'success')
        
        # Verificar se a solicitação veio de eventos ou de outra página
        referrer = request.referrer
        if referrer and 'events' in referrer:
            return redirect(url_for('main.events'))
        else:
            return redirect(url_for('main.calendar'))
    else:
        if form.errors:
            print(f"Erros de validação: {form.errors}")
        
    return render_template('calendar/event_form.html', form=form, title='Novo Evento')

@main.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    # Permitir apenas o criador do evento ou o admin da família
    if event.family_id != current_user.active_family_id or (event.user_id != current_user.id and current_user not in event.family.admins):
        flash('Você não tem permissão para editar este evento.', 'error')
        return redirect(url_for('main.calendar'))
    form = EventForm()
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        db.session.commit()
        flash('Evento atualizado com sucesso!', 'success')
        return redirect(url_for('main.calendar'))
    elif request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.start_time.data = event.start_time
        form.end_time.data = event.end_time
    return render_template('calendar/event_form.html', form=form, title='Editar Evento')

@main.route('/event/<int:event_id>/delete')
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    # Permitir apenas o criador do evento ou o admin da família
    if event.family_id != current_user.active_family_id or (event.user_id != current_user.id and current_user not in event.family.admins):
        flash('Você não tem permissão para excluir este evento.', 'error')
        return redirect(url_for('main.calendar'))
    
    db.session.delete(event)
    db.session.commit()
    flash('Evento excluído com sucesso!', 'success')
    return redirect(url_for('main.calendar'))

@main.route('/family/members')
@login_required
def family_members():
    if not current_user.active_family_id:
        return redirect(url_for('main.family_options'))
    
    # Obter a família ativa
    active_family = Family.query.get(current_user.active_family_id)
    members = active_family.members.all()
    
    # Gerar link de convite se o usuário for admin
    invite_link = None
    if current_user in active_family.admins:
        invite_link = url_for('main.join_family', token=active_family.get_join_token(), _external=True)
    
    return render_template('family/family_members.html', members=members, invite_link=invite_link)

@main.route('/family/make_admin/<int:user_id>')
@login_required
def make_admin(user_id):
    if not current_user.active_family_id:
        flash('Você precisa pertencer a um grupo familiar.', 'error')
        return redirect(url_for('main.calendar'))
    
    if current_user not in current_user.active_family.admins:
        flash('Apenas administradores podem promover outros membros.', 'error')
        return redirect(url_for('main.family_members'))
    
    user = User.query.get_or_404(user_id)
    active_family = Family.query.get(current_user.active_family_id)
    
    # Verificar se o usuário pertence à família ativa
    if not user in active_family.members.all():
        flash('Este usuário não pertence à sua família.', 'error')
        return redirect(url_for('main.family_members'))
    
    if user in active_family.admins:
        flash('Este usuário já é um administrador.', 'info')
    else:
        active_family.admins.append(user)
        db.session.commit()
        flash(f'{user.username} agora é um administrador do grupo.', 'success')
    
    return redirect(url_for('main.family_members'))

@main.route('/family/remove_admin/<int:user_id>')
@login_required
def remove_admin(user_id):
    if not current_user.active_family_id or current_user not in current_user.active_family.admins:
        flash('Você não tem permissão para realizar esta ação.', 'error')
        return redirect(url_for('main.family_members'))
    
    user = User.query.get_or_404(user_id)
    active_family = Family.query.get(current_user.active_family_id)
    
    # Verificar se o usuário pertence à família ativa
    if not user in active_family.members.all():
        flash('Este usuário não pertence à sua família.', 'error')
        return redirect(url_for('main.family_members'))
    
    if user == current_user:
        flash('Você não pode remover seus próprios privilégios de administrador.', 'error')
        return redirect(url_for('main.family_members'))
    
    if user in active_family.admins:
        active_family.admins.remove(user)
        db.session.commit()
        flash(f'Privilégios de administrador removidos de {user.username}.', 'success')
    else:
        flash('Este usuário não é um administrador.', 'info')
    
    return redirect(url_for('main.family_members'))

@main.route('/family/remove_member/<int:user_id>')
@login_required
def remove_member(user_id):
    if not current_user.active_family_id or current_user not in current_user.active_family.admins:
        flash('Você não tem permissão para realizar esta ação.', 'error')
        return redirect(url_for('main.family_members'))
    
    user = User.query.get_or_404(user_id)
    active_family = Family.query.get(current_user.active_family_id)
    
    # Verificar se o usuário pertence à família ativa
    if not user in active_family.members.all():
        flash('Este usuário não pertence à sua família.', 'error')
        return redirect(url_for('main.family_members'))
    
    if user == current_user:
        flash('Você não pode remover a si mesmo do grupo.', 'error')
        return redirect(url_for('main.family_members'))
    
    # Remover privilégios de admin se tiver
    if user in active_family.admins:
        active_family.admins.remove(user)
    
    # Remover da família
    active_family.members.remove(user)
    
    # Se esta era a família ativa do usuário, definir como nulo
    if user.active_family_id == active_family.id:
        user.active_family_id = None
        
    db.session.commit()
    flash(f'{user.username} foi removido do grupo familiar.', 'success')
    
    return redirect(url_for('main.family_members'))

@main.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if not current_user.active_family_id:
        return redirect(url_for('main.family_options'))
    
    form = TaskForm()
    
    # Adiciona os membros da família e a opção "todos"
    active_family = Family.query.get(current_user.active_family_id)
    family_members = active_family.members.all()
    form.assigned_to_id.choices = [(0, 'Todos')] + [(user.id, user.username) for user in family_members]
    
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data if form.description.data else None,
            due_date=form.due_date.data,
            user_id=current_user.id,
            family_id=current_user.active_family_id,
            assigned_to_id=form.assigned_to_id.data if form.assigned_to_id.data != 0 else None
        )
        db.session.add(task)
        db.session.commit()
        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('main.tasks'))
    
    tasks = Task.query.filter_by(family_id=current_user.active_family_id).order_by(Task.due_date.asc()).all()
    return render_template('tasks/tasks.html', tasks=tasks, form=form)

@main.route('/tasks/complete/<int:task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.family_id != current_user.active_family_id:
        flash('Você não tem permissão para alterar esta tarefa.', 'error')
        return redirect(url_for('main.tasks'))
    
    task.completed = True
    db.session.commit()
    flash('Tarefa marcada como concluída!', 'success')
    return redirect(url_for('main.tasks'))

@main.route('/tasks/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.family_id != current_user.active_family_id or (task.user_id != current_user.id and current_user not in current_user.active_family.admins):
        flash('Você não tem permissão para excluir esta tarefa.', 'error')
        return redirect(url_for('main.tasks'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Tarefa excluída com sucesso!', 'success')
    return redirect(url_for('main.tasks'))

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        family_name = request.form.get('family_name')
        if family_name and current_user.active_family:
            current_user.active_family.name = family_name
            db.session.commit()
            flash('Configurações atualizadas com sucesso!', 'success')
            return redirect(url_for('main.settings'))
    
    return render_template('user/settings.html')

@main.route('/settings/clean_past_events', methods=['POST'])
@login_required
def clean_past_events_manual():
    if not current_user.active_family_id:
        return redirect(url_for('main.family_options'))
    
    if current_user not in current_user.active_family.admins:
        flash('Apenas administradores podem limpar eventos antigos.', 'error')
        return redirect(url_for('main.settings'))
    
    removed_count = clean_past_events(current_user.active_family_id)
    
    if removed_count > 0:
        flash(f'{removed_count} eventos antigos foram removidos com sucesso!', 'success')
    else:
        flash('Não foram encontrados eventos antigos para remover.', 'info')
    
    return redirect(url_for('main.settings'))

# API para tarefas (para uso futuro com AJAX se necessário)
@main.route('/api/tasks', methods=['GET'])
@login_required
def api_tasks():
    if not current_user.active_family_id:
        return jsonify({'error': 'No family group'}), 403
    
    tasks = Task.query.filter_by(family_id=current_user.active_family_id).all()
    result = []
    
    for task in tasks:
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'completed': task.completed,
            'created_by': task.user.username,
            'assigned_to': task.assigned_to.username if task.assigned_to else None
        })
    
    return jsonify(result)

@main.route('/api/tasks', methods=['POST'])
@login_required
def api_create_task():
    if not current_user.active_family_id:
        return jsonify({'error': 'No family group'}), 403
    
    data = request.json
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    # Verifica se o assigned_to_id pertence à família
    assigned_to_id = data.get('assigned_to_id')
    if assigned_to_id:
        user = User.query.get(assigned_to_id)
        active_family = Family.query.get(current_user.active_family_id)
        if not user or not user in active_family.members.all():
            return jsonify({'error': 'Invalid assigned user'}), 400
    
    task = Task(
        title=data.get('title'),
        description=data.get('description', ''),
        due_date=datetime.fromisoformat(data.get('due_date')) if data.get('due_date') else None,
        user_id=current_user.id,
        family_id=current_user.active_family_id,
        assigned_to_id=assigned_to_id
    )
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'id': task.id,
        'message': 'Task created successfully'
    }), 201

@main.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def api_update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.family_id != current_user.active_family_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Atualiza apenas os campos fornecidos
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'due_date' in data and data['due_date']:
        task.due_date = datetime.fromisoformat(data['due_date'])
    if 'completed' in data:
        task.completed = bool(data['completed'])
    if 'assigned_to_id' in data:
        # Verifica se o usuário existe e pertence à família
        if data['assigned_to_id']:
            user = User.query.get(data['assigned_to_id'])
            active_family = Family.query.get(current_user.active_family_id)
            if not user or not user in active_family.members.all():
                return jsonify({'error': 'Invalid assigned user'}), 400
        task.assigned_to_id = data['assigned_to_id']
    
    db.session.commit()
    return jsonify({'message': 'Task updated successfully'})

@main.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.family_id != current_user.active_family_id or (task.user_id != current_user.id and current_user not in current_user.active_family.admins):
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'})

@main.route('/dashboard')
@login_required
def dashboard():
    if not current_user.active_family_id:
        return redirect(url_for('main.family_options'))
    
    today = date.today()
    
    # Eventos do dia
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    todays_events = Event.query.filter_by(family_id=current_user.active_family_id).filter(
        Event.start_time.between(today_start, today_end)
    ).all()
    
    # Eventos futuros (próximos 7 dias)
    week_end = today_start + timedelta(days=7)
    upcoming_events = Event.query.filter_by(family_id=current_user.active_family_id).filter(
        Event.start_time.between(today_start, week_end)
    ).order_by(Event.start_time).all()
    
    # Tarefas pendentes atribuídas ao usuário atual
    my_tasks = Task.query.filter_by(
        assigned_to_id=current_user.id, 
        completed=False,
        family_id=current_user.active_family_id
    ).order_by(Task.due_date).all()
    
    # Tarefas familiares pendentes
    family_tasks = Task.query.filter_by(
        family_id=current_user.active_family_id,
        completed=False
    ).filter(Task.assigned_to_id != current_user.id).order_by(Task.due_date).all()
    
    # Membros da família
    active_family = Family.query.get(current_user.active_family_id)
    family_members = active_family.members.all()
    
    return render_template('dashboard/dashboard.html',
                          today=today,
                          todays_events=todays_events,
                          upcoming_events=upcoming_events,
                          my_tasks=my_tasks,
                          family_tasks=family_tasks,
                          family_members=family_members)

@main.route('/imagens/<filename>')
def imagens(filename):
    return send_from_directory('../frontend/static/images', filename)

@main.route('/family/options')
@login_required
def family_options():
    return render_template('family/family_options.html')

@main.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    if not current_user.active_family_id:
        return redirect(url_for('main.family_options'))
    
    # Criar o formulário para o modal
    form = EventForm()
    
    # Verificar se o formulário foi enviado e é válido
    if form.validate_on_submit():
        try:
            event = Event(
                title=form.title.data,
                description=form.description.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                user_id=current_user.id,
                family_id=current_user.active_family_id
            )
            db.session.add(event)
            db.session.commit()
            flash('Evento criado com sucesso!', 'success')
            return redirect(url_for('main.events'))
        except Exception as e:
            flash(f'Erro ao criar evento: {str(e)}', 'error')
    
    # Buscar todos os eventos da família
    events = Event.query.filter_by(family_id=current_user.active_family_id).order_by(Event.start_time.asc()).all()
    
    return render_template('eventos/events.html', events=events, form=form)

@main.route('/leave_family', methods=['POST'])
@login_required
def leave_family():
    if not current_user.active_family_id:
        flash('Você não pertence a nenhum grupo familiar.', 'error')
        return redirect(url_for('main.family_options'))
    
    active_family = Family.query.get(current_user.active_family_id)
    
    # Remover privilégios de admin se tiver
    if current_user in active_family.admins:
        active_family.admins.remove(current_user)
    
    # Remover da família
    active_family.members.remove(current_user)
    
    # Limpar família ativa
    current_user.active_family_id = None
    db.session.commit()
    
    flash(f'Você saiu do grupo familiar {active_family.name}.', 'success')
    return redirect(url_for('main.family_options'))

@main.route('/delete_family', methods=['POST'])
@login_required
def delete_family():
    if not current_user.active_family_id:
        flash('Você não pertence a nenhum grupo familiar.', 'error')
        return redirect(url_for('main.family_options'))
    
    active_family = Family.query.get(current_user.active_family_id)
    
    # Verificar se o usuário é administrador
    if current_user not in active_family.admins:
        flash('Apenas administradores podem excluir um grupo familiar.', 'error')
        return redirect(url_for('main.settings'))
    
    # Armazenar o nome para exibir na mensagem
    family_name = active_family.name
    
    # Remover todos os eventos da família
    Event.query.filter_by(family_id=active_family.id).delete()
    
    # Remover todas as tarefas da família
    Task.query.filter_by(family_id=active_family.id).delete()
    
    # Limpar família ativa de todos os membros
    for member in active_family.members:
        if member.active_family_id == active_family.id:
            member.active_family_id = None
    
    # Remover a família
    db.session.delete(active_family)
    db.session.commit()
    
    flash(f'O grupo familiar {family_name} foi excluído com sucesso.', 'success')
    return redirect(url_for('main.family_options'))

@main.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    email = request.form.get('email')
    
    if not username or not email:
        flash('Nome de usuário e email são obrigatórios', 'error')
        return redirect(url_for('main.calendar'))
    
    # Verificar se o email já está em uso
    existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
    if existing_user:
        flash('Este email já está em uso por outro usuário', 'error')
        return redirect(url_for('main.calendar'))
    
    current_user.username = username
    current_user.email = email
    db.session.commit()
    
    flash('Perfil atualizado com sucesso!', 'success')
    return redirect(url_for('main.calendar')) 
