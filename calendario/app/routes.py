from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
import calendar as cal_module
import os
from app import db
from app.models import User, Family, Event, Message
from app.forms import LoginForm, RegistrationForm, FamilyForm, EventForm, MessageForm, ProfileForm

main = Blueprint('main', __name__)

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
            flash('Login falhou. Verifique seu email e senha.')
    return render_template('login.html', form=form)

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
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Conta criada com sucesso! Agora você pode fazer login.')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from flask import current_app
    
    form = ProfileForm()
    if form.validate_on_submit():
        # Removemos o processamento de imagens do Pillow e apenas armazenamos o nome do usuário
        # que servirá para exibição de iniciais ou nome como avatar
        current_user.username = form.username.data
        db.session.commit()
        flash('Perfil atualizado com sucesso!')
        return redirect(url_for('main.profile'))
        
    elif request.method == 'GET':
        form.username.data = current_user.username
        
    return render_template('profile.html', form=form)

# Rotas da família
@main.route('/create_family', methods=['GET', 'POST'])
@login_required
def create_family():
    form = FamilyForm()
    if form.validate_on_submit():
        family = Family(
            name=form.name.data,
            admin_id=current_user.id
        )
        db.session.add(family)
        db.session.commit()
        family.admins.append(current_user)
        db.session.commit()
        current_user.family = family
        db.session.commit()
        flash('Grupo familiar criado com sucesso!')
        return redirect(url_for('main.calendar'))
    return render_template('create_family.html', form=form)

@main.route('/join_family/<token>')
@login_required
def join_family(token):
    family = Family.verify_join_token(token)
    if not family:
        flash('Link inválido ou expirado!')
        return redirect(url_for('main.calendar'))
    
    current_user.family_id = family.id
    db.session.commit()
    flash(f'Você entrou no grupo familiar {family.name}!')
    return redirect(url_for('main.calendar'))

@main.route('/invite')
@login_required
def invite():
    if not current_user.family or current_user not in current_user.family.admins:
        flash('Você precisa ser o administrador de um grupo familiar para convidar pessoas.')
        return redirect(url_for('main.calendar'))
    
    token = current_user.family.get_join_token()
    invite_link = url_for('main.join_family', token=token, _external=True)
    return render_template('invite.html', invite_link=invite_link)

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
            flash('Link de convite inválido!')
    return render_template('join_family.html')

# Rotas do calendário
@main.route('/')
@main.route('/calendar')
@login_required
def calendar():
    if not current_user.family:
        # Renderiza o calendário vazio com aviso
        return render_template('calendar.html', events=[], upcoming_events=[], days_in_month=0, first_day_of_month=0, current_year=datetime.now().year, current_month=datetime.now().month, no_family=True)
    
    # Obter mês atual
    today = date.today()
    year = today.year
    month = today.month
    
    # Obter informações do calendário para o mês atual
    monthly_calendar = cal_module.monthcalendar(year, month)
    first_day_of_month = cal_module.monthrange(year, month)[0]
    days_in_month = cal_module.monthrange(year, month)[1]
    
    # Buscar todos os eventos do mês atual para a família do usuário
    events = Event.query.filter_by(family_id=current_user.family_id).all()
    
    # Filtrar eventos futuros para a seção de próximos eventos
    upcoming_events = [event for event in events if event.start_time >= datetime.now()]
    upcoming_events.sort(key=lambda x: x.start_time)
    
    return render_template('calendar.html', 
                          events=events, 
                          upcoming_events=upcoming_events,
                          days_in_month=days_in_month,
                          first_day_of_month=first_day_of_month,
                          current_year=year,
                          current_month=month)

@main.route('/event/new', methods=['GET', 'POST'])
@login_required
def new_event():
    if not current_user.family:
        flash('Você precisa pertencer a um grupo familiar para criar eventos.')
        return redirect(url_for('main.calendar'))
    
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            user_id=current_user.id,
            family_id=current_user.family_id
        )
        db.session.add(event)
        db.session.commit()
        flash('Evento criado com sucesso!')
        return redirect(url_for('main.calendar'))
        
    return render_template('event_form.html', form=form, title='Novo Evento')

@main.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    # Permitir apenas o criador do evento ou o admin da família
    if event.family_id != current_user.family_id or (event.user_id != current_user.id and current_user not in current_user.family.admins):
        flash('Você não tem permissão para editar este evento.')
        return redirect(url_for('main.calendar'))
    form = EventForm()
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        db.session.commit()
        flash('Evento atualizado com sucesso!')
        return redirect(url_for('main.calendar'))
    elif request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.start_time.data = event.start_time
        form.end_time.data = event.end_time
    return render_template('event_form.html', form=form, title='Editar Evento')

@main.route('/event/<int:event_id>/delete')
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    # Permitir apenas o criador do evento ou o admin da família
    if event.family_id != current_user.family_id or (event.user_id != current_user.id and current_user not in current_user.family.admins):
        flash('Você não tem permissão para excluir este evento.')
        return redirect(url_for('main.calendar'))
    db.session.delete(event)
    db.session.commit()
    flash('Evento excluído com sucesso!')
    return redirect(url_for('main.calendar'))

# Rotas do chat
@main.route('/chat')
@login_required
def chat():
    if not current_user.family:
        flash('Você precisa pertencer a um grupo familiar para acessar o chat.')
        return redirect(url_for('main.calendar'))
    
    form = MessageForm()
    messages = Message.query.filter_by(family_id=current_user.family_id).order_by(Message.timestamp).all()
    return render_template('chat.html', form=form, messages=messages)

@main.route('/send_message', methods=['POST'])
@login_required
def send_message():
    if not current_user.family:
        flash('Você precisa pertencer a um grupo familiar para enviar mensagens.')
        return redirect(url_for('main.calendar'))
    
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            content=form.content.data,
            user_id=current_user.id,
            family_id=current_user.family_id
        )
        db.session.add(message)
        db.session.commit()
    return redirect(url_for('main.chat'))

@main.route('/family/members')
@login_required
def family_members():
    if not current_user.family:
        flash('Você não pertence a um grupo familiar.')
        return redirect(url_for('main.calendar'))
    members = current_user.family.members
    is_admin = current_user in current_user.family.admins
    return render_template('family_members.html', members=members, is_admin=is_admin)

@main.route('/family/make_admin/<int:user_id>')
@login_required
def make_admin(user_id):
    family = current_user.family
    if not family or current_user not in family.admins:
        flash('Apenas administradores podem promover outros membros.')
        return redirect(url_for('main.family_members'))
    user = next((m for m in family.members if m.id == user_id), None)
    if not user:
        flash('Usuário não encontrado.')
        return redirect(url_for('main.family_members'))
    if user in family.admins:
        flash('Este usuário já é administrador.')
        return redirect(url_for('main.family_members'))
    family.admins.append(user)
    from app import db
    db.session.commit()
    flash(f'{user.username} agora é administrador!')
    return redirect(url_for('main.family_members')) 