from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from app import db
from app.models import User
from app.dispatcher_auth import bp
from app.dispatcher_auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from REST import DispatcherApi
from Helper import Config, Log


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        def _exist():
            if User.query.filter_by(username=form.username.data).first() is not None:
                form.username.errors.append("Username already registered")
                return True
            elif User.query.filter_by(email=form.email.data).first() is not None:
                form.email.errors.append("Email already registered")
                return True
            else:
                return False

        if _exist():
            return render_template('dispatcher_auth/register.html', title='Register', form=form,
                                   description=Config().Description, ewEnabled=Config().EastWest.Enabled)

        user: User = User(username=form.username.data, email=form.email.data, organization=form.organization.data)
        user.setPassword(form.password.data)

        try:
            response = DispatcherApi().Register(user)
            result = response["result"]
        except Exception as e:
            result = f"Exception while accessing authentication: {e}"

        if "User registered" in result:
            db.session.add(user)
            db.session.commit()
            flash(result, 'info')
            return redirect(url_for('auth.login'))
        else:
            flash(result, 'error')

    return render_template('dispatcher_auth/register.html', title='Register', form=form,
                           description=Config().Description, ewEnabled=Config().EastWest.Enabled)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        Log.I(f'The user is already authenticated')
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Check that the user exists in the Portal database
        user: User = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.checkPassword(form.password.data):
            Log.I(f'Invalid username or password')
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))

        # Check that the user exist in the dispatcher DB and has been activated
        DispatcherApi().RenewUserToken(user)
        if user.token is None:
            flash(f"Could not retrieve authentication token", "error")
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.rememberMe.data)
        Log.I(f'User {user.username} logged in')
        nextPage = request.args.get('next')
        if not nextPage or url_parse(nextPage).netloc != '':
            nextPage = url_for('main.index')

        return redirect(nextPage)

    return render_template('dispatcher_auth/login.html', title='Sign In', form=form,
                           description=Config().Description, ewEnabled=Config().EastWest.Enabled)


@bp.route('/logout')
def logout():
    logout_user()
    Log.I(f'User logged out')
    return redirect(url_for('main.index'))
