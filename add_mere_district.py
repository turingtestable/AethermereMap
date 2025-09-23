#!/usr/bin/env python3
"""
Add The Mere as district 0 to the database.
"""

from app import create_app, db
from app.models import District

def add_mere_district():
    app = create_app()
    with app.app_context():
        # Check if The Mere already exists
        mere = District.query.filter_by(district_number=0).first()
        if not mere:
            mere = District(
                district_number=0,
                name='The Mere',
                info='The dark pool at the center of Aethermere, where the great crystal spire once stood. After The Weeping, this became a void of swirling dark water that seems to absorb light itself.',
                status='Forbidden',
                color='#1a202c',
                svg_path='circle',
                label_x=200,
                label_y=205
            )
            db.session.add(mere)
            db.session.commit()
            print("✅ Added The Mere as district 0")
        else:
            print("✅ The Mere already exists")

if __name__ == '__main__':
    add_mere_district()