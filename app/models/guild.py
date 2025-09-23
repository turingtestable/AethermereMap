from app import db
from datetime import datetime

class Guild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    leadership = db.Column(db.String(200), nullable=True)  # Who leads the guild
    headquarters_district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=True)
    status = db.Column(db.String(50), nullable=True)  # Active, Disbanded, Underground, etc.
    influence = db.Column(db.String(20), nullable=True)  # Low, Medium, High
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to district
    headquarters = db.relationship('District', backref=db.backref('guilds', lazy=True))
    
    def __repr__(self):
        return f'<Guild {self.name}>'

class GuildRelationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guild_1_id = db.Column(db.Integer, db.ForeignKey('guild.id'), nullable=False)
    guild_2_id = db.Column(db.Integer, db.ForeignKey('guild.id'), nullable=False)
    relationship_type = db.Column(db.String(20), nullable=False)  # 'positive' or 'negative'
    description = db.Column(db.Text, nullable=True)  # Details about the relationship
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships to guilds
    guild_1 = db.relationship('Guild', foreign_keys=[guild_1_id], backref='relationships_as_first')
    guild_2 = db.relationship('Guild', foreign_keys=[guild_2_id], backref='relationships_as_second')
    
    # Ensure we don't have duplicate relationships (guild A -> guild B and guild B -> guild A)
    __table_args__ = (db.UniqueConstraint('guild_1_id', 'guild_2_id', name='unique_guild_relationship'),)
    
    def __repr__(self):
        return f'<GuildRelationship {self.guild_1.name} -> {self.guild_2.name} ({self.relationship_type})>'
    
    @classmethod
    def get_guild_relationships(cls, guild_id):
        """Get all relationships for a specific guild"""
        return cls.query.filter(
            (cls.guild_1_id == guild_id) | (cls.guild_2_id == guild_id)
        ).all()
    
    @classmethod
    def get_relationship_between(cls, guild_1_id, guild_2_id):
        """Get the relationship between two specific guilds"""
        return cls.query.filter(
            ((cls.guild_1_id == guild_1_id) & (cls.guild_2_id == guild_2_id)) |
            ((cls.guild_1_id == guild_2_id) & (cls.guild_2_id == guild_1_id))
        ).first()