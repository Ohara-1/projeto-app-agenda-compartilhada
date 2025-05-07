from backend import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=True)
    events = db.relationship('Event', backref='creator', lazy=True)
    
    def get_calendars(self):
        """Retorna o calendário (família) ao qual o usuário pertence"""
        if hasattr(self, 'family') and self.family:
            return [self.family]
        return []
    
    def set_active_calendar(self, family_id):
        """Define o calendário ativo para o usuário"""
        self.family_id = family_id
        db.session.commit()

family_admins = db.Table('family_admins',
    db.Column('family_id', db.Integer, db.ForeignKey('family.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    events = db.relationship('Event', backref='family', lazy=True)
    admins = db.relationship('User', secondary=family_admins, backref='admin_families')
    members = db.relationship('User', backref=db.backref('family', overlaps="admin_families"),
                            foreign_keys=[User.family_id])
    
    def get_join_token(self, expires_sec=86400):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'family_id': self.id})
    
    @staticmethod
    def verify_join_token(token):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=86400)  # token expira após 24 horas
            family_id = data['family_id']
        except:
            return None
        return Family.query.get(family_id)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relacionamentos
    user = db.relationship('User', foreign_keys=[user_id], backref='created_tasks')
    family = db.relationship('Family', backref='tasks')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_tasks') 
