from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import District, User
from app import db
import os

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    districts = District.query.order_by(District.district_number).all()
    return render_template('index.html', districts=districts)

@bp.route('/guilds')
@login_required
def guilds():
    # Only DMs and admins can access guild management
    if not current_user.can_edit_districts():
        return "Access denied. Only DMs and Admins can access guild management.", 403
    
    return render_template('guilds.html')

@bp.route('/guild-info')
@login_required
def guild_info():
    # All users can access guild information
    return render_template('guild_info.html')