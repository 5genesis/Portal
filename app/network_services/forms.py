from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class BaseNsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    public = SelectField('Visibility', choices=[('Public', 'Public'), ('Private', 'Private')])


class NewNsForm(BaseNsForm):
    create = SubmitField('Create')


class EditNsForm(BaseNsForm):
    update = SubmitField('Update')

    preloadVnfd = SubmitField('Pre-load')
    selectVndf = SubmitField('Select')

    preloadVim = SubmitField('Pre-load')
    onboardVim = SubmitField('Onboard')
    deleteVim = SubmitField('Delete')
    selectVim = SubmitField('Select')

    preloadNsd = SubmitField('Pre-load')
    onboardNsd = SubmitField('Onboard')
    deleteNsd = SubmitField('Delete')
    selectNsd = SubmitField('Select')

    closeAction = SubmitField('Commit')
    cancelAction = SubmitField('Cancel')
