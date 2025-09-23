from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, CharacterQuickRef
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


@bp.route('/quick-reference', methods=['GET', 'POST'])
@login_required
def quick_reference():
    if current_user.role != 'player':
        flash('Access denied. Quick reference is only available to players.', 'error')
        return redirect(url_for('main.index'))

    # Get or create quick reference for current user
    quick_ref = CharacterQuickRef.query.filter_by(user_id=current_user.id).first()
    if not quick_ref:
        quick_ref = CharacterQuickRef(user_id=current_user.id)
        db.session.add(quick_ref)
        db.session.commit()

    if request.method == 'POST':
        try:
            # Update character name (in user table)
            character_name = request.form.get('character_name', '').strip()
            if character_name == '':
                current_user.character_name = None
            else:
                if len(character_name) > 100:
                    flash('Character name must be 100 characters or less.', 'error')
                    return render_template('auth/quick_reference.html', quick_ref=quick_ref)
                current_user.character_name = character_name

            # Update evasion score
            evasion = request.form.get('evasion_score')
            quick_ref.evasion_score = int(evasion) if evasion and evasion.strip() else None

            # Update damage thresholds
            damage_thresholds = {
                'minor': int(request.form.get('minor_threshold')) if request.form.get('minor_threshold') else None,
                'major': int(request.form.get('major_threshold')) if request.form.get('major_threshold') else None,
                'severe': int(request.form.get('severe_threshold')) if request.form.get('severe_threshold') else None
            }
            quick_ref.set_damage_thresholds(damage_thresholds)

            # Update experiences (2-4 items)
            experiences = []
            for i in range(1, 5):  # Support up to 4 experiences
                exp = request.form.get(f'experience_{i}', '').strip()
                if exp:
                    experiences.append(exp)

            # Ensure at least 2 experiences
            while len(experiences) < 2:
                experiences.append('')

            quick_ref.set_experiences(experiences)

            # Update class and specialization
            quick_ref.class_name = request.form.get('class_name', '').strip() or None
            quick_ref.specialization = request.form.get('specialization', '').strip() or None

            db.session.commit()
            flash('Quick reference updated successfully!', 'success')
            return redirect(url_for('auth.quick_reference'))

        except (ValueError, TypeError) as e:
            flash('Invalid input. Please check your entries.', 'error')

    return render_template('auth/quick_reference.html', quick_ref=quick_ref)


@bp.route('/admin/quick-references')
@login_required
def admin_quick_references():
    if current_user.role not in ['admin', 'dm']:
        flash('Access denied. Admin or DM privileges required.', 'error')
        return redirect(url_for('main.index'))

    # Get all players with their quick references
    players = User.query.filter_by(role='player').all()

    return render_template('auth/admin_quick_references.html', players=players)


@bp.route('/admin/quick-references/<int:user_id>', methods=['PUT'])
@login_required
def update_player_quick_ref(user_id):
    if current_user.role not in ['admin', 'dm']:
        return jsonify({'error': 'Access denied'}), 403

    user = User.query.get_or_404(user_id)
    if user.role != 'player':
        return jsonify({'error': 'User is not a player'}), 400

    # Get or create quick reference
    quick_ref = CharacterQuickRef.query.filter_by(user_id=user_id).first()
    if not quick_ref:
        quick_ref = CharacterQuickRef(user_id=user_id)
        db.session.add(quick_ref)

    try:
        data = request.get_json()

        # Update character name in user table
        if 'character_name' in data:
            character_name = data['character_name']
            if character_name and len(character_name) > 100:
                return jsonify({'error': 'Character name must be 100 characters or less'}), 400
            user.character_name = character_name

        # Update quick reference fields
        quick_ref.evasion_score = data.get('evasion_score')

        if 'damage_thresholds' in data:
            quick_ref.set_damage_thresholds(data['damage_thresholds'])

        if 'experiences' in data:
            quick_ref.set_experiences(data['experiences'])

        quick_ref.class_name = data.get('class_name')
        quick_ref.specialization = data.get('specialization')

        db.session.commit()
        return jsonify({'message': 'Quick reference updated successfully', 'quick_ref': quick_ref.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400