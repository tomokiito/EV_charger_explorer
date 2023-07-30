from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Search')