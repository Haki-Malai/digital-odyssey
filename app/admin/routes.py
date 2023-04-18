import os
from flask import current_app, render_template, url_for, redirect, request, \
    flash, g
from flask_login import login_required

from app.admin import bp
from app.models import Category
from app.decorators import admin_required
from app.admin.forms import ColorForm


def allowed_file(filename: str) -> bool:
    """Check if the file is allowed to be uploaded.
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() \
            in current_app.config['ALLOWED_EXTENSIONS']


@bp.before_app_request
def before_request() -> None:
    """Set the config object to the global config.
    """
    g.config = current_app.config


@bp.route('/admin')
def index() -> str:
    """Redirect to the admin dashboard.
    """
    return redirect(url_for('admin.main', screen='dashboard'))


@bp.route('/admin/<screen>')
@login_required
@admin_required
def main(screen) -> str:
    """Admin main page.
    """
    return render_template(f'admin/{screen}.html',
                           screen=screen,
                           categories=Category.query.all())


@bp.route('/admin/design')
@login_required
@admin_required
def design() -> str:
    """Design page.
    """
    form = ColorForm()
    return render_template('admin/design.html',
                           colors_form=form,
                           screen='design',
                           categories=Category.query.all())


@bp.route('/admin/logo', methods=['POST'])
@login_required
@admin_required
def upload_logo() -> str:
    """Upload a logo.
    """
    if 'logo' not in request.files:
        flash('No file part', 'warning')
        return redirect(url_for('admin.main', screen='design'))
    logo = request.files['logo']
    if logo.filename == '':
        flash('No selected file', 'warning')
        return redirect(url_for('admin.main', screen='design'))
    if logo and allowed_file(logo.filename):
        filename = 'general/logo.png'
        logo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('admin.main', screen='design'))


@bp.route('/admin/colors', methods=['POST'])
@login_required
@admin_required
def colors() -> str:
    """Update the colors.
    """
    form = ColorForm()
    if form.validate_on_submit():
        for key, value in form.data.items():
            if 'color' in key.lower() and value:
                current_app.config_obj.update_config(key, value)
        flash('Colors updated successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.title()} field {error}', 'error')
    return redirect(url_for('admin.main', screen='design'))
