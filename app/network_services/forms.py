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
    preloadVnfd = SubmitField('Pre-load')

    location = SelectField('VIM Location', choices=[('Main DC', 'Main DC'), ('Edge DC', 'Edge DC')])
    updateLocation = SubmitField('Update')
    preloadVim = SubmitField('Pre-load')

    preloadNsd = SubmitField('Pre-load')

