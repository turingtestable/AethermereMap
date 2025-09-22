from flask import Blueprint, jsonify, request
from app import db
from app.models import District

bp = Blueprint('api', __name__)

@bp.route('/districts', methods=['GET'])
def get_districts():
    districts = District.query.all()
    return jsonify([district.to_dict() for district in districts])

@bp.route('/districts/<int:district_id>', methods=['GET', 'PUT', 'DELETE'])
def district_detail(district_id):
    district = District.query.get_or_404(district_id)
    if request.method == 'PUT':
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