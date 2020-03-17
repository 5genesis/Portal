from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class NewNsForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired()])
    public = SelectField('public', choices=[('Public', 'Public'), ('Private', 'Private')])
    submit = SubmitField('Create')
