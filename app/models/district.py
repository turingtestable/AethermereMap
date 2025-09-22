from app import db
from datetime import datetime

class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Always need a name
    info = db.Column(db.Text, nullable=True)  # Can be null for TBD districts
    status = db.Column(db.String(50), nullable=True)  # Can be null initially
    color = db.Column(db.String(20), nullable=False, default='#4a5568')  # Default gray for TBD
    district_number = db.Column(db.Integer, nullable=False, unique=True)  # Always need the number
    
    # SVG path data for the district shape
    svg_path = db.Column(db.Text, nullable=False)  # Always need the shape
    
    # Coordinates for the district label
    label_x = db.Column(db.Integer, nullable=False)  # Always need label position
    label_y = db.Column(db.Integer, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<District {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'info': self.info,
            'status': self.status,
            'color': self.color,
            'district_number': self.district_number,
            'svg_path': self.svg_path,
            'label_x': self.label_x,
            'label_y': self.label_y,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }