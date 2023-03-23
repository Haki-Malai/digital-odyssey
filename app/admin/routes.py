from flask import current_app, render_template, url_for, redirect
from flask_login import login_required

from app.admin import bp
from app.models import Category
from app.decorators import admin_required


@bp.route('/admin')
def index():
    return redirect(url_for('admin.main', screen='dashboard'))


@bp.route('/admin/<screen>')
@login_required
@admin_required
def main(screen):
    return render_template(f'admin/{screen}.html',
                           screen=screen,
                           config=current_app.config,
                           categories=Category.query.all())