from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import District, PlayerNote, Guild, GuildRelationship

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
        district_data = district.to_dict()
        
        # Add guild information for this district
        district_data['guilds'] = []
        
        # Get guilds headquartered in this district
        headquartered_guilds = Guild.query.filter_by(headquarters_district_id=district.id).all()
        for guild in headquartered_guilds:
            guild_data = {
                'id': guild.id,
                'name': guild.name,
                'description': guild.description,
                'leadership': guild.leadership,
                'status': guild.status,
                'influence': guild.influence,
                'relationship_to_district': 'headquartered'
            }
            district_data['guilds'].append(guild_data)
        
        # Get city-wide guilds (guilds with no specific headquarters)
        citywide_guilds = Guild.query.filter_by(headquarters_district_id=None).all()
        for guild in citywide_guilds:
            guild_data = {
                'id': guild.id,
                'name': guild.name,
                'description': guild.description,
                'leadership': guild.leadership,
                'status': guild.status,
                'influence': guild.influence,
                'relationship_to_district': 'citywide'
            }
            district_data['guilds'].append(guild_data)
        
        return jsonify(district_data)
    
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

# Guild API endpoints

@bp.route('/guilds', methods=['GET'])
@login_required
def get_guilds():
    """Get all guilds"""
    guilds = Guild.query.all()
    guilds_data = []
    
    for guild in guilds:
        guild_data = {
            'id': guild.id,
            'name': guild.name,
            'description': guild.description,
            'leadership': guild.leadership,
            'status': guild.status,
            'influence': guild.influence,
            'headquarters_district_id': guild.headquarters_district_id,
            'headquarters_name': guild.headquarters.name if guild.headquarters else None,
            'created_at': guild.created_at.isoformat(),
            'updated_at': guild.updated_at.isoformat()
        }
        guilds_data.append(guild_data)
    
    return jsonify(guilds_data)

@bp.route('/guilds/<int:guild_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def guild_detail(guild_id):
    """Get, update, or delete a specific guild"""
    guild = Guild.query.get_or_404(guild_id)
    
    if request.method == 'GET':
        # Get guild relationships
        relationships = GuildRelationship.get_guild_relationships(guild_id)
        relationships_data = []
        
        for rel in relationships:
            other_guild = rel.guild_2 if rel.guild_1_id == guild_id else rel.guild_1
            relationships_data.append({
                'id': rel.id,
                'other_guild_id': other_guild.id,
                'other_guild_name': other_guild.name,
                'relationship_type': rel.relationship_type,
                'description': rel.description
            })
        
        guild_data = {
            'id': guild.id,
            'name': guild.name,
            'description': guild.description,
            'leadership': guild.leadership,
            'status': guild.status,
            'influence': guild.influence,
            'headquarters_district_id': guild.headquarters_district_id,
            'headquarters_name': guild.headquarters.name if guild.headquarters else None,
            'relationships': relationships_data,
            'created_at': guild.created_at.isoformat(),
            'updated_at': guild.updated_at.isoformat()
        }
        
        return jsonify(guild_data)
    
    elif request.method == 'PUT':
        # Only DMs and Admins can edit guilds
        if not current_user.can_edit_districts():  # Using same permission as districts
            return jsonify({'error': 'Permission denied. Only DMs and Admins can edit guilds.'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Update guild fields
        for field in ['name', 'description', 'leadership', 'status', 'influence', 'headquarters_district_id']:
            if field in data:
                setattr(guild, field, data[field])
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Guild updated successfully'})
    
    elif request.method == 'DELETE':
        # Only Admins can delete guilds
        if current_user.role != 'admin':
            return jsonify({'error': 'Permission denied. Only Admins can delete guilds.'}), 403
        
        # Delete related relationships first
        relationships = GuildRelationship.query.filter(
            (GuildRelationship.guild_1_id == guild_id) | 
            (GuildRelationship.guild_2_id == guild_id)
        ).all()
        
        for rel in relationships:
            db.session.delete(rel)
        
        db.session.delete(guild)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Guild deleted successfully'})

@bp.route('/guilds', methods=['POST'])
@login_required
def create_guild():
    """Create a new guild"""
    # Only DMs and Admins can create guilds
    if not current_user.can_edit_districts():
        return jsonify({'error': 'Permission denied. Only DMs and Admins can create guilds.'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Guild name is required'}), 400
    
    # Check if guild name already exists
    existing_guild = Guild.query.filter_by(name=name).first()
    if existing_guild:
        return jsonify({'error': 'A guild with this name already exists'}), 400
    
    guild = Guild(
        name=name,
        description=data.get('description', ''),
        leadership=data.get('leadership', ''),
        status=data.get('status', 'Active'),
        influence=data.get('influence', 'Medium'),
        headquarters_district_id=data.get('headquarters_district_id')
    )
    
    db.session.add(guild)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Guild created successfully',
        'guild_id': guild.id
    })

# Guild Relationship API endpoints

@bp.route('/guild-relationships', methods=['GET'])
@login_required
def get_guild_relationships():
    """Get all guild relationships"""
    relationships = GuildRelationship.query.all()
    relationships_data = []
    
    for rel in relationships:
        relationships_data.append({
            'id': rel.id,
            'guild_1_id': rel.guild_1_id,
            'guild_1_name': rel.guild_1.name,
            'guild_2_id': rel.guild_2_id,
            'guild_2_name': rel.guild_2.name,
            'relationship_type': rel.relationship_type,
            'description': rel.description,
            'created_at': rel.created_at.isoformat(),
            'updated_at': rel.updated_at.isoformat()
        })
    
    return jsonify(relationships_data)

@bp.route('/guild-relationships', methods=['POST'])
@login_required
def create_guild_relationship():
    """Create a new guild relationship"""
    # Only DMs and Admins can create relationships
    if not current_user.can_edit_districts():
        return jsonify({'error': 'Permission denied. Only DMs and Admins can manage guild relationships.'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    guild_1_id = data.get('guild_1_id')
    guild_2_id = data.get('guild_2_id')
    relationship_type = data.get('relationship_type')
    
    if not all([guild_1_id, guild_2_id, relationship_type]):
        return jsonify({'error': 'Guild IDs and relationship type are required'}), 400
    
    if relationship_type not in ['positive', 'negative']:
        return jsonify({'error': 'Relationship type must be "positive" or "negative"'}), 400
    
    if guild_1_id == guild_2_id:
        return jsonify({'error': 'A guild cannot have a relationship with itself'}), 400
    
    # Check if relationship already exists
    existing_rel = GuildRelationship.get_relationship_between(guild_1_id, guild_2_id)
    if existing_rel:
        return jsonify({'error': 'A relationship between these guilds already exists'}), 400
    
    # Verify guilds exist
    guild_1 = Guild.query.get(guild_1_id)
    guild_2 = Guild.query.get(guild_2_id)
    
    if not guild_1 or not guild_2:
        return jsonify({'error': 'One or both guilds do not exist'}), 400
    
    relationship = GuildRelationship(
        guild_1_id=guild_1_id,
        guild_2_id=guild_2_id,
        relationship_type=relationship_type,
        description=data.get('description', '')
    )
    
    db.session.add(relationship)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Guild relationship created successfully',
        'relationship_id': relationship.id
    })

@bp.route('/guild-relationships/<int:relationship_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_guild_relationship(relationship_id):
    """Update or delete a guild relationship"""
    # Only DMs and Admins can manage relationships
    if not current_user.can_edit_districts():
        return jsonify({'error': 'Permission denied. Only DMs and Admins can manage guild relationships.'}), 403
    
    relationship = GuildRelationship.query.get_or_404(relationship_id)
    
    if request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Update relationship fields
        if 'relationship_type' in data:
            if data['relationship_type'] not in ['positive', 'negative']:
                return jsonify({'error': 'Relationship type must be "positive" or "negative"'}), 400
            relationship.relationship_type = data['relationship_type']
        
        if 'description' in data:
            relationship.description = data['description']
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Guild relationship updated successfully'})
    
    elif request.method == 'DELETE':
        db.session.delete(relationship)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Guild relationship deleted successfully'})