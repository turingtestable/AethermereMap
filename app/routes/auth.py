from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = bool(request.form.get('remember_me'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/admin/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    users = User.query.order_by(User.username).all()
    return render_template('auth/manage_users.html', users=users)

@bp.route('/admin/users/create', methods=['POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'player')
    
    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    if role not in ['admin', 'dm', 'player']:
        return jsonify({'error': 'Invalid role'}), 400
    
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    })

@bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'})

@bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_user_password(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot reset your own password'}), 400
    
    # Set password to a default value
    default_password = 'welcome123'
    user.set_password(default_password)
    db.session.commit()
    
    return jsonify({
        'message': f'Password reset for {user.username}',
        'new_password': default_password
    })

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Validate current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html')
        
        # Validate new password
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'error')
            return render_template('auth/change_password.html')
        
        # Validate password confirmation
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('auth/change_password.html')
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/change_password.html')

@bp.route('/character-profile', methods=['GET', 'POST'])
@login_required
def character_profile():
    if current_user.role != 'player':
        flash('Access denied. Character profiles are only available to players.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        character_name = request.form['character_name'].strip()
        
        # Allow empty character name (clears it)
        if character_name == '':
            current_user.character_name = None
        else:
            # Validate character name length
            if len(character_name) > 100:
                flash('Character name must be 100 characters or less.', 'error')
                return render_template('auth/character_profile.html')
            current_user.character_name = character_name
        
        db.session.commit()
        flash('Character profile updated successfully!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/character_profile.html')