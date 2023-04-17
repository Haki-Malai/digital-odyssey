from flask import redirect, url_for

from app.api import bp


@bp.route('/docs')
def docs():
    return redirect(url_for('apifairy.docs'))