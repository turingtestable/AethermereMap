from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import District, PlayerNote

bp = Blueprint('api', __name__)

@bp.route('/districts', methods=['GET'])
@login_required
def get_districts():
    districts = District.query.all()
    return jsonify([district.to_dict() for district in districts])

@bp.route('/districts/<int:district_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def district_detail(district_id):
    district = District.query.get_or_404(district_id)
    
    if request.method == 'PUT':
        # Only DMs and Admins can edit districts
        if not current_user.can_edit_districts():
            return jsonify({'error': 'Permission denied. Only DMs and Admins can edit districts.'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        for k,v in data.items():
            setattr(district, k,v)
        db.session.commit()
        return jsonify({'success':True, 'district': district.to_dict()})
    
    elif request.method == 'GET':
        return jsonify(district.to_dict())
    
    else:
        return jsonify({'message': f'District {district_id} detail'})

# Player Notes API endpoints

@bp.route('/notes/<target_type>/<int:target_id>', methods=['GET'])
@login_required
def get_notes(target_type, target_id):
    """Get all notes for a specific target (district or guild)"""
    if target_type not in ['district', 'guild']:
        return jsonify({'error': 'Invalid target type'}), 400
    
    notes = PlayerNote.get_notes_for_target(target_type, target_id)
    
    notes_data = []
    for note in notes:
        notes_data.append({
            'id': note.id,
            'user_id': note.user_id,
            'username': note.user.username,
            'content': note.content,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat()
        })
    
    return jsonify(notes_data)

@bp.route('/notes', methods=['POST'])
@login_required
def create_note():
    """Create a new player note"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    target_type = data.get('target_type')
    target_id = data.get('target_id')
    content = data.get('content', '').strip()
    
    if target_type not in ['district', 'guild']:
        return jsonify({'error': 'Invalid target type'}), 400
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    if not target_id:
        return jsonify({'error': 'Target ID is required'}), 400
    
    # Check if user already has a note for this target
    existing_note = PlayerNote.get_user_note_for_target(
        current_user.id, target_type, target_id
    )
    
    if existing_note:
        # Update existing note instead of creating new one
        existing_note.content = content
        db.session.commit()
        
        return jsonify({
            'message': 'Note updated successfully',
            'note': {
                'id': existing_note.id,
                'content': existing_note.content,
                'updated_at': existing_note.updated_at.isoformat()
            }
        })
    else:
        # Create new note
        note = PlayerNote(
            user_id=current_user.id,
            target_type=target_type,
            target_id=target_id,
            content=content
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify({
            'message': 'Note created successfully',
            'note': {
                'id': note.id,
                'content': note.content,
                'created_at': note.created_at.isoformat()
            }
        })

@bp.route('/notes/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    """Update a player note"""
    note = PlayerNote.query.get_or_404(note_id)
    
    # Only the note owner or admin can edit
    if note.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    note.content = content
    db.session.commit()
    
    return jsonify({
        'message': 'Note updated successfully',
        'note': {
            'id': note.id,
            'content': note.content,
            'updated_at': note.updated_at.isoformat()
        }
    })

@bp.route('/notes/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    """Delete a player note"""
    note = PlayerNote.query.get_or_404(note_id)
    
    # Only the note owner or admin can delete
    if note.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({'message': 'Note deleted successfully'})