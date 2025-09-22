from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import District

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