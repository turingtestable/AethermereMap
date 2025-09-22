#!/usr/bin/env python3
"""
Script to create users for the Aethermere Map application.
Usage: python create_user.py <username> <email> <password> <role>
Roles: admin, dm, player
"""

import sys
from app import create_app, db
from app.models import User

def create_user(username, email, password, role='player'):
    app = create_app()
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            print(f"User '{username}' already exists!")
            return False
        
        if User.query.filter_by(email=email).first():
            print(f"Email '{email}' already in use!")
            return False
        
        # Validate role
        if role not in ['admin', 'dm', 'player']:
            print(f"Invalid role '{role}'. Must be: admin, dm, or player")
            return False
        
        # Create user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ Created {role} user: {username} ({email})")
        return True

if __name__ == '__main__':
    if len(sys.argv) not in [4, 5]:
        print("Usage: python create_user.py <username> <email> <password> [role]")
        print("Roles: admin, dm, player (default: player)")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    role = sys.argv[4] if len(sys.argv) == 5 else 'player'
    
    create_user(username, email, password, role)