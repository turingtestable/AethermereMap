#!/usr/bin/env python3
"""
Initialize production database with districts and admin user.
Run this once after deployment.
"""

import os
from app import create_app, db
from app.models import District, User

# District data
districts_data = [
    {
        'district_number': 1, 'name': 'District 1', 'info': 'To be determined as the campaign develops.',
        'status': 'Unknown', 'color': '#4a5568', 'svg_path': 'M 200,200 L 236,67 A 140,140 0 0,1 299,101 Z',
        'label_x': 268, 'label_y': 88
    },
    {
        'district_number': 2, 'name': 'District 2', 'info': 'To be determined as the campaign develops.',
        'status': 'Unknown', 'color': '#4a5568', 'svg_path': 'M 200,200 L 299,101 A 140,140 0 0,1 333,158 Z',
        'label_x': 316, 'label_y': 130
    },
    {
        'district_number': 3, 'name': 'Dawnward (3rd)', 
        'info': 'Sealed District - Dangerous magical effects from The Weeping. Ratmen stronghold underneath.',
        'status': 'Sealed - Dangerous', 'color': 'sealed', 'svg_path': 'M 200,200 L 333,158 A 140,140 0 0,1 333,242 Z',
        'label_x': 333, 'label_y': 200
    },
    {
        'district_number': 4, 'name': 'District 4', 'info': 'To be determined as the campaign develops.',
        'status': 'Unknown', 'color': '#4a5568', 'svg_path': 'M 200,200 L 333,242 A 140,140 0 0,1 299,299 Z',
        'label_x': 316, 'label_y': 270
    },
    {
        'district_number': 5, 'name': 'Goldmark (5th)', 'info': 'Commercial heart - Guild halls, markets, active trade.',
        'status': 'Active', 'color': '#d69e2e', 'svg_path': 'M 200,200 L 299,299 A 140,140 0 0,1 236,333 Z',
        'label_x': 268, 'label_y': 312
    },
    {
        'district_number': 6, 'name': 'Greywater (6th)', 
        'info': 'Working class, docks. Renamed from Brightwater after The Weeping.',
        'status': 'Struggling', 'color': '#2b6cb0', 'svg_path': 'M 200,200 L 236,333 A 140,140 0 0,1 164,333 Z',
        'label_x': 200, 'label_y': 325
    },
    {
        'district_number': 7, 'name': 'District 7', 'info': 'To be determined as the campaign develops.',
        'status': 'Unknown', 'color': '#4a5568', 'svg_path': 'M 200,200 L 164,333 A 140,140 0 0,1 101,299 Z',
        'label_x': 132, 'label_y': 312
    },
    {
        'district_number': 8, 'name': 'District 8', 'info': 'To be determined as the campaign develops.',
        'status': 'Unknown', 'color': '#4a5568', 'svg_path': 'M 200,200 L 101,299 A 140,140 0 0,1 67,242 Z',
        'label_x': 84, 'label_y': 270
    },
    {
        'district_number': 9, 'name': 'District 9', 'info': 'To be determined as the campaign develops.',
        'status': 'Unknown', 'color': '#4a5568', 'svg_path': 'M 200,200 L 67,242 A 140,140 0 0,1 67,158 Z',
        'label_x': 67, 'label_y': 200
    },
    {
        'district_number': 10, 'name': 'District 10', 'info': 'To be determined as the campaign develops.',
        'status': 'Unknown', 'color': '#4a5568', 'svg_path': 'M 200,200 L 67,158 A 140,140 0 0,1 101,101 Z',
        'label_x': 84, 'label_y': 130
    },
    {
        'district_number': 11, 'name': 'District 11', 'info': 'To be determined as the campaign develops.',
        'status': 'Unknown', 'color': '#4a5568', 'svg_path': 'M 200,200 L 101,101 A 140,140 0 0,1 164,67 Z',
        'label_x': 132, 'label_y': 88
    },
    {
        'district_number': 12, 'name': 'District 12', 'info': 'To be determined as the campaign develops.',
        'status': 'Unknown', 'color': '#4a5568', 'svg_path': 'M 200,200 L 164,67 A 140,140 0 0,1 236,67 Z',
        'label_x': 200, 'label_y': 67
    }
]

def init_production():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add districts if they don't exist
        if District.query.count() == 0:
            for district_data in districts_data:
                district = District(**district_data)
                db.session.add(district)
            print(f"✅ Added {len(districts_data)} districts")
        
        # Create admin user if it doesn't exist
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@aethermere.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'change-me-in-production')
        
        if not User.query.filter_by(username=admin_username).first():
            admin = User(username=admin_username, email=admin_email, role='admin')
            admin.set_password(admin_password)
            db.session.add(admin)
            print(f"✅ Created admin user: {admin_username}")
        
        db.session.commit()
        print("🚀 Production database initialized!")

if __name__ == '__main__':
    init_production()