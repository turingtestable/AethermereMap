from flask import Blueprint, render_template
from app.models import District

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    districts = District.query.order_by(District.district_number).all()
    return render_template('index.html', districts=districts)