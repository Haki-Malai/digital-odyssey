import os
from flask import current_app, render_template, url_for, redirect, request, \
    flash
from werkzeug.utils import secure_filename
from flask_login import login_required

from app.admin import bp
from app.models import Category
from app.decorators import admin_required


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() \
            in current_app.config['ALLOWED_EXTENSIONS']


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


@bp.route('/admin/logo', methods=['POST'])
@login_required
@admin_required
def upload_logo():
    if 'logo' not in request.files:
        flash('No file part', 'warning')
        return redirect(url_for('admin.main', screen='design'))
    file = request.files['logo']
    if file.filename == '':
        flash('No selected file', 'warning')
        return redirect(url_for('admin.main', screen='design'))
    if file and allowed_file(file.filename):
        filename = 'general/logo.png'
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('admin.main', screen='design'))