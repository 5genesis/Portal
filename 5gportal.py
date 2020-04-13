from typing import Dict
from app import create_app, db
from app.models import User, Experiment, Execution, Action
from Helper import Config

app = create_app()
config = Config()


@app.shell_context_processor
def make_shell_context() -> Dict:
    return {'DB': db, 'User': User, 'Experiment': Experiment, 'Execution': Execution, 'Action': Action, 'Config': config}
