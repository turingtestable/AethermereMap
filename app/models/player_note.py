from app import db
from datetime import datetime

class PlayerNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # 'district' or 'guild'
    target_id = db.Column(db.Integer, nullable=False)  # ID of district or guild
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('notes', lazy=True))
    
    def __repr__(self):
        return f'<PlayerNote {self.user.username} on {self.target_type} {self.target_id}>'
    
    @classmethod
    def get_notes_for_target(cls, target_type, target_id):
        """Get all notes for a specific target (district or guild)"""
        return cls.query.filter_by(
            target_type=target_type, 
            target_id=target_id
        ).order_by(cls.updated_at.desc()).all()
    
    @classmethod
    def get_user_note_for_target(cls, user_id, target_type, target_id):
        """Get a specific user's note for a target"""
        return cls.query.filter_by(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id
        ).first()