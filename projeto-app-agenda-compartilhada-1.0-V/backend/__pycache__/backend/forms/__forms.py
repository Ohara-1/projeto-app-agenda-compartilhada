from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from backend.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Cadastrar')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está registrado. Por favor, escolha outro.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha',
                             validators=[DataRequired()])
    remember = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')

class ProfileForm(FlaskForm):
    username = StringField('Nome de Usuário',
                           validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Atualizar')

class FamilyForm(FlaskForm):
    name = StringField('Nome do Grupo Familiar',
                      validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Criar Grupo')

class EventForm(FlaskForm):
    title = StringField('Título',
                        validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Descrição')
    start_time = DateTimeField('Início (YYYY-MM-DD HH:MM)', 
                               format='%Y-%m-%d %H:%M',
                               validators=[DataRequired()])
    end_time = DateTimeField('Fim (YYYY-MM-DD HH:MM)', 
                             format='%Y-%m-%d %H:%M',
                             validators=[DataRequired()])
    submit = SubmitField('Salvar Evento')
    
    def validate_end_time(self, end_time):
        if end_time.data < self.start_time.data:
            raise ValidationError('O horário de término deve ser posterior ao horário de início.')

class MessageForm(FlaskForm):
    content = TextAreaField('Mensagem', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class TaskForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField('Descrição')
    due_date = DateTimeField('Data e Hora', format='%Y-%m-%d %H:%M')
    assigned_to_id = SelectField('Atribuir para', coerce=int)
    submit = SubmitField('Adicionar') 