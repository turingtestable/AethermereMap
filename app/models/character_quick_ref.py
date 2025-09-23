from app import db
from datetime import datetime
import json


class CharacterQuickRef(db.Model):
    __tablename__ = 'character_quick_refs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    evasion_score = db.Column(db.Integer, nullable=True)
    damage_thresholds = db.Column(db.Text, nullable=True)  # JSON string for minor/major/severe
    experiences = db.Column(db.Text, nullable=True)  # JSON array of experiences
    class_name = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to user
    user = db.relationship('User', backref=db.backref('character_quick_ref', uselist=False))

    def __repr__(self):
        return f'<CharacterQuickRef {self.user.username}>'

    def get_damage_thresholds(self):
        """Parse damage thresholds from JSON string"""
        if self.damage_thresholds:
            try:
                return json.loads(self.damage_thresholds)
            except (json.JSONDecodeError, TypeError):
                return {"minor": None, "major": None, "severe": None}
        return {"minor": None, "major": None, "severe": None}

    def set_damage_thresholds(self, thresholds_dict):
        """Set damage thresholds as JSON string"""
        if thresholds_dict:
            self.damage_thresholds = json.dumps(thresholds_dict)
        else:
            self.damage_thresholds = None

    def get_experiences(self):
        """Parse experiences from JSON string"""
        if self.experiences:
            try:
                return json.loads(self.experiences)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def set_experiences(self, experiences_list):
        """Set experiences as JSON string"""
        if experiences_list:
            # Ensure we have 2-4 experiences
            if len(experiences_list) < 2:
                experiences_list = experiences_list + [""] * (2 - len(experiences_list))
            elif len(experiences_list) > 4:
                experiences_list = experiences_list[:4]
            self.experiences = json.dumps(experiences_list)
        else:
            self.experiences = json.dumps(["", ""])  # Default to 2 empty experiences

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'character_name': self.user.character_name,
            'evasion_score': self.evasion_score,
            'damage_thresholds': self.get_damage_thresholds(),
            'experiences': self.get_experiences(),
            'class_name': self.class_name,
            'specialization': self.specialization,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }