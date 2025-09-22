#!/usr/bin/env python3
"""
Fix District 12 label positioning to be centered like Greywater.
"""

from app import create_app, db
from app.models import District

def fix_district12():
    app = create_app()
    with app.app_context():
        # Find District 12
        district12 = District.query.filter_by(district_number=12).first()
        
        if district12:
            # Center it horizontally like Greywater (x=200) and adjust y slightly
            district12.label_x = 200
            district12.label_y = 67  # Keep y the same or adjust as needed
            
            db.session.commit()
            print(f"✅ Fixed District 12 label position: x={district12.label_x}, y={district12.label_y}")
        else:
            print("❌ District 12 not found")

if __name__ == '__main__':
    fix_district12()