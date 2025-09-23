from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False, default='player')  # 'admin', 'dm', 'player'
    character_name = db.Column(db.String(100), nullable=True)  # Character name for display
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete timestamp
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def soft_delete(self):
        """Mark user as deleted"""
        self.deleted_at = datetime.utcnow()

    def is_deleted(self):
        """Check if user is soft deleted"""
        return self.deleted_at is not None

    @classmethod
    def get_active_users(cls):
        """Get all non-deleted users"""
        return cls.query.filter(cls.deleted_at.is_(None))

    @classmethod
    def get_active_players(cls):
        """Get all non-deleted players"""
        return cls.query.filter(cls.deleted_at.is_(None), cls.role == 'player')
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_dm(self):
        return self.role in ['admin', 'dm']
    
    @property
    def is_player(self):
        return self.role == 'player'
    
    def can_edit_districts(self):
        return self.role in ['admin', 'dm']
    
    def can_invite_users(self):
        return self.role == 'admin'
    
    @property
    def display_name(self):
        """Return 'Username (Character Name)' format, or just username if no character name"""
        if self.character_name:
            return f"{self.username} ({self.character_name})"
        return self.username
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))