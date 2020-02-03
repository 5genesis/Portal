from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from app import db
from app.models import User
from app.authentication import bp
from app.authentication.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.authentication.email import sendPasswordResetEmail
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

        Log.D(f'Registration form data - Username: {form.username.data}, Email: {form.email.data},'
              f' Organization: {form.organization.data}')

        if _exist():
            return render_template('authentication/register.html', title='Register', form=form,
                                   description=Config().Description)

        user: User = User(username=form.username.data, email=form.email.data, organization=form.organization.data)
        user.setPassword(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have been registered', 'info')
        Log.I(f'Registered user: {user.username}')
        return redirect(url_for('auth.login'))

    return render_template('authentication/register.html', title='Register', form=form,
                           description=Config().Description)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        Log.I(f'The user is already authenticated')
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user: User = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.checkPassword(form.password.data):
            Log.I(f'Invalid username or password')
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.rememberMe.data)
        Log.I(f'User {user.username} logged in')
        nextPage = request.args.get('next')
        if not nextPage or url_parse(nextPage).netloc != '':
            nextPage = url_for('main.index')
        return redirect(nextPage)

    return render_template('authentication/login.html', title='Sign In', form=form,
                           description=Config().Description)


@bp.route('/logout')
def logout():
    logout_user()
    Log.I(f'User logged out')
    return redirect(url_for('main.index'))


@bp.route('/resetPasswordRequest', methods=['GET', 'POST'])
def resetPasswordRequest():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user: User = User.query.filter_by(email=form.email.data).first()
        if user:
            sendPasswordResetEmail(user)

        flash('Check your email for the instructions to reset your password', 'info')
        return redirect(url_for('auth.login'))

    return render_template('authentication/resetPasswordRequest.html',
                           title='Reset Password', form=form, description=Config().Description)


@bp.route('/resetPassword/<token>', methods=['GET', 'POST'])
def resetPassword(token: str):
    if current_user.is_authenticated:
        Log.I(f'The user is already authenticated')
        return redirect(url_for('main.index'))

    user: User = User.verifyResetPasswordToken(token)
    if not user:
        Log.I(f'Reset password token do not match any user')
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.setPassword(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'info')
        Log.I(f'Password reset for {user.name}')
        return redirect(url_for('auth.login'))

    return render_template('authentication/resetPassword.html', form=form, description=Config().Description)
