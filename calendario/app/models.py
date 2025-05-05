from app import db, login_manager
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
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    events = db.relationship('Event', backref='creator', lazy=True)
    messages = db.relationship('Message', backref='author', lazy=True)

family_admins = db.Table('family_admins',
    db.Column('family_id', db.Integer, db.ForeignKey('family.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    members = db.relationship('User', backref='family', lazy=True, foreign_keys=[User.family_id])
    events = db.relationship('Event', backref='family', lazy=True)
    messages = db.relationship('Message', backref='family', lazy=True)
    admins = db.relationship('User', secondary=family_admins, backref='admin_families')
    
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

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False) 