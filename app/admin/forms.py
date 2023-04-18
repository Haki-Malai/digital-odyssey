import re
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError


class ColorForm(FlaskForm):
    """Color form.
    """
    submit = SubmitField()
    black_color = StringField()
    bg_gray_color = StringField()
    border_color = StringField()
    border_color_2 = StringField()
    dark_color = StringField()
    gray_color = StringField()
    gray_color_2 = StringField()
    light_color = StringField()
    light_color_2 = StringField()
    secondary_color = StringField()
    secondary_color_2 = StringField()
    sky_color = StringField()
    text_gray_color = StringField()
    theme_color = StringField()
    theme_color_2 = StringField()
    theme_color_3 = StringField()
    theme_color_4 = StringField()
    white_color = StringField()
    yellow_color = StringField()
