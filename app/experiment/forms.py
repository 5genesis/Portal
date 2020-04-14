from flask_wtf import FlaskForm
from wtforms import SubmitField


class ExperimentForm(FlaskForm):
    submit = SubmitField('Add experiment')


class RunExperimentForm(FlaskForm):
    submit = SubmitField('Run experiment')
