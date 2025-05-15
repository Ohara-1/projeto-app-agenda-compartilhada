from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateTimeField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from backend.models.models import User
from flask_login import current_user

# Mensagens personalizadas em português
class CustomValidators:
    class DataRequired(DataRequired):
        def __init__(self, message=None):
            super().__init__(message=message or 'Este campo é obrigatório.')
            
    class Length(Length):
        def __init__(self, min=-1, max=-1, message=None):
            message = message or f'Este campo deve ter entre {min} e {max} caracteres.' if min != -1 and max != -1 else None
            if min != -1 and max == -1 and not message:
                message = f'Este campo deve ter pelo menos {min} caracteres.'
            if max != -1 and min == -1 and not message:
                message = f'Este campo não pode ter mais que {max} caracteres.'
            super().__init__(min=min, max=max, message=message)
    
    class Email(Email):
        def __init__(self, message=None):
            super().__init__(message=message or 'Insira um endereço de email válido.')
            
    class EqualTo(EqualTo):
        def __init__(self, fieldname, message=None):
            super().__init__(fieldname, message=message or 'Os campos devem ser iguais.')

class RegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', 
                           validators=[CustomValidators.DataRequired(), CustomValidators.Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[CustomValidators.DataRequired(), CustomValidators.Email()])
    password = PasswordField('Senha',
                             validators=[CustomValidators.DataRequired()])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[CustomValidators.DataRequired(), CustomValidators.EqualTo('password')])
    submit = SubmitField('Cadastrar')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está registrado. Por favor, escolha outro.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[CustomValidators.DataRequired(), CustomValidators.Email()])
    password = PasswordField('Senha',
                             validators=[CustomValidators.DataRequired()])
    remember = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')

class ProfileForm(FlaskForm):
    username = StringField('Nome de Usuário',
                           validators=[CustomValidators.DataRequired(), CustomValidators.Length(min=2, max=20)])
    submit = SubmitField('Atualizar')

class FamilyForm(FlaskForm):
    name = StringField('Nome do Grupo Familiar',
                      validators=[CustomValidators.DataRequired(), CustomValidators.Length(min=2, max=100)])
    submit = SubmitField('Criar Grupo')

class EventForm(FlaskForm):
    title = StringField('Título',
                        validators=[CustomValidators.DataRequired(), CustomValidators.Length(min=2, max=100)])
    description = TextAreaField('Descrição')
    start_time = DateTimeField('Início', 
                               format='%Y-%m-%d %H:%M',
                               validators=[CustomValidators.DataRequired()])
    end_time = DateTimeField('Fim', 
                             format='%Y-%m-%d %H:%M',
                             validators=[CustomValidators.DataRequired()])
    submit = SubmitField('Salvar Evento')
    
    def validate_end_time(self, end_time):
        if end_time.data < self.start_time.data:
            raise ValidationError('O horário de término deve ser posterior ao horário de início.')

class TaskForm(FlaskForm):
    title = StringField('Título', validators=[CustomValidators.DataRequired(), CustomValidators.Length(min=2, max=120)])
    description = TextAreaField('Descrição', validators=[Optional()])
    due_date = DateField('Data', format='%Y-%m-%d', validators=[CustomValidators.DataRequired()])
    assigned_to_id = SelectField('Atribuir para', coerce=int, validators=[])
    submit = SubmitField('Adicionar')
