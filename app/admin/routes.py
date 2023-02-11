from flask import render_template
from flask_login import login_required
from app.admin import bp
from app.decorators import admin_required

@bp.route('/admin', methods=['GET'])
@login_required
@admin_required
def index():
    return render_template('dashboard/index.html')