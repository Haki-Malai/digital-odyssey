from flask import render_template, current_app, redirect, \
    url_for, flash, Response, g
from flask_login import login_required, login_user, logout_user

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.decorators import logout_required
from app.models import User, Category

LOGIN_ROUTE: str = 'auth.login'
MAIN_ROUTE: str = 'main.index'


@bp.before_app_request
def before_request() -> None:
    """Set search form to the global config.
    """
    g.config = current_app.config


@bp.route('/login')
@logout_required
def login() -> str:
    """Get the login page.
    """
    login_form = LoginForm()

    return render_template('auth/login.html',
                           login_form=login_form,
                           categories=Category.query.all())


@bp.route('/login', methods=['POST'])
@logout_required
def submit_login() -> Response:
    """Login the user.
    """
    login_form = LoginForm()

    if not login_form.validate_on_submit():
        return redirect(url_for(LOGIN_ROUTE))

    user = User.query.filter_by(email=login_form.entity.data).first() or \
        User.query.filter_by(username=login_form.entity.data).first()

    if user is None or not user.verify_password(login_form.password.data):
        flash('Invalid username or password', 'danger')
        return redirect(url_for(LOGIN_ROUTE))

    login_user(user, remember=login_form.remember_me.data)
    return redirect(url_for(MAIN_ROUTE))


@bp.route('/logout')
@login_required
def logout() -> Response:
    """Logout the current user.
    """
    logout_user()
    return redirect(url_for(MAIN_ROUTE))


@bp.route('/register')
def register() -> str:
    """Get the registration page.
    """
    registration_form = RegistrationForm()

    return render_template('auth/register.html',
                           registration_form=registration_form)


@bp.route('/register', methods=['POST'])
@logout_required
def submit_register() -> Response:
    """Register a new user.
    """
    registration_form = RegistrationForm()
    if not registration_form.validate_on_submit():
        for error in registration_form.errors:
            flash(registration_form.errors[error][0], 'danger')
            return redirect(url_for('auth.submit_register'))

    user = User(username=registration_form.username.data,
                email=registration_form.email.data)
    user.set_password(registration_form.password.data)
    db.session.add(user)
    db.session.commit()

    flash('Congratulations, you are now a registered user!', 'success')
    return redirect(url_for(LOGIN_ROUTE))


@bp.route('/reset_password_request')
def reset_password_request() -> str:
    """Get the reset password request page.
    """
    return render_template('auth/reset_password_request.html')
