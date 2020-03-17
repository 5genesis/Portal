from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class BaseNsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    public = SelectField('Visibility', choices=[('Public', 'Public'), ('Private', 'Private')])


class NewNsForm(BaseNsForm):
    create = SubmitField('Create')


class EditNsForm(BaseNsForm):
    update = SubmitField('Update')
    other = SubmitField('Other')
