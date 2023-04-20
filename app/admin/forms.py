import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError


def validate_color(form:FlaskForm, field:object):
    """Validate color format.
    :param form: The form to validate.
    :param field: The field to validate.
    """
    if field.data and not re.match(r'^#[0-9A-Fa-f]{6}$', field.data):
        raise ValidationError('Invalid color format. Must be in the form #123123')


class ColorForm(FlaskForm):
    """Color form.
    """
    submit = SubmitField()
    black_color = StringField(validators=[validate_color])
    bg_gray_color = StringField(validators=[validate_color])
    border_color = StringField(validators=[validate_color])
    border_color_2 = StringField(validators=[validate_color])
    dark_color = StringField(validators=[validate_color])
    gray_color = StringField(validators=[validate_color])
    gray_color_2 = StringField(validators=[validate_color])
    light_color = StringField(validators=[validate_color])
    light_color_2 = StringField(validators=[validate_color])
    secondary_color = StringField(validators=[validate_color])
    secondary_color_2 = StringField(validators=[validate_color])
    sky_color = StringField(validators=[validate_color])
    text_gray_color = StringField(validators=[validate_color])
    theme_color = StringField(validators=[validate_color])
    theme_color_2 = StringField(validators=[validate_color])
    theme_color_3 = StringField(validators=[validate_color])
    theme_color_4 = StringField(validators=[validate_color])
    white_color = StringField(validators=[validate_color])
    yellow_color = StringField(validators=[validate_color])
