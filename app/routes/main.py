from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import District

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    districts = District.query.order_by(District.district_number).all()
    return render_template('index.html', districts=districts)