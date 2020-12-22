from flask_wtf import FlaskForm
from wtforms import SubmitField


class ExperimentForm(FlaskForm):
    submit = SubmitField('Add experiment')


class RunExperimentForm(FlaskForm):
    submit = SubmitField('Run experiment')


class DistributedStep1Form(FlaskForm):
    submit = SubmitField('Continue')


class DistributedStep2Form(ExperimentForm):
    pass
