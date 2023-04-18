from flask import redirect, url_for

from app.api import bp


@bp.route('/docs')
def docs() -> str:
    """Redirect to the API documentation.
    """
    return redirect(url_for('apifairy.docs'))
