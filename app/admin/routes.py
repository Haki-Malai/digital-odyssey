import os
from flask import current_app, render_template, url_for, redirect, request, \
    flash, g
from flask_login import login_required

from app import update_config
from app.admin import bp
from app.models import Category
from app.decorators import admin_required
from app.admin.forms import ColorForm, GeneralForm

MAIN_ROUTE: str = 'admin.main'


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
    return redirect(url_for(MAIN_ROUTE, screen='dashboard'))


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
    color_form = ColorForm()
    general_form = GeneralForm()
    return render_template('admin/design.html',
                           colors_form=color_form,
                           general_form=general_form,
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
        return redirect(url_for(MAIN_ROUTE, screen='design'))
    logo = request.files['logo']
    if logo.filename == '':
        flash('No selected file', 'warning')
        return redirect(url_for(MAIN_ROUTE, screen='design'))
    if logo and allowed_file(logo.filename):
        filename = 'general/logo.png'
        logo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for(MAIN_ROUTE, screen='design'))


@bp.route('/admin/colors', methods=['POST'])
@login_required
@admin_required
def colors() -> str:
    """Update the colors.
    """
    color_form = ColorForm()
    if color_form.validate_on_submit():
        for key, value in color_form.data.items():
            if 'color' in key.lower() and value:
                current_app.config_obj.update_config(key, value)
                update_config(current_app, 'default')
        flash('Colors updated successfully!', 'success')
    else:
        for field, errors in color_form.errors.items():
            for error in errors:
                flash(f'{field.title()} field {error}', 'error')
    return redirect(url_for(MAIN_ROUTE, screen='design'))


@bp.route('/admin/general', methods=['POST'])
@login_required
@admin_required
def general() -> str:
    """Update the general settings.
    """
    general_form = GeneralForm()
    if general_form.validate_on_submit():
        for key, value in general_form.data.items():
            if key in general_form.items and value:
                current_app.config_obj.update_config(key, value)
                update_config(current_app, 'default')
        flash('General settings updated successfully!', 'success')
    else:
        for field, errors in general_form.errors.items():
            for error in errors:
                flash(f'{field.title()} field {error}', 'error')
    return redirect(url_for(MAIN_ROUTE, screen='design'))
