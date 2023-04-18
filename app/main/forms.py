from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    """Search form.
    """
    q = StringField(('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form.
        """
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)
