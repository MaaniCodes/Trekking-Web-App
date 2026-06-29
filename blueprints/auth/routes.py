from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from blueprints.auth import auth_bp
from blueprints.auth.forms import LoginForm, RegisterForm
from extensions import db
from models import User, ROLE_ADMIN, ROLE_STAFF, ROLE_TREKKER


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard_redirect'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            role=form.role.data,
            phone=form.phone.data.strip() or None,
            city=form.city.data.strip() or None,
        )
        user.set_password(form.password.data)

        # Staff accounts need admin approval before dashboard access
        if user.role == ROLE_STAFF:
            user.is_staff_approved = False

        db.session.add(user)
        db.session.commit()

        if user.role == ROLE_STAFF:
            flash('Account created! Your guide profile is pending admin approval.', 'info')
        else:
            flash('Welcome to Hikers Hub! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard_redirect'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html', form=form)

        if user.is_blacklisted:
            flash('This account has been suspended. Please contact admin.', 'danger')
            return render_template('auth/login.html', form=form)

        login_user(user, remember=form.remember.data)
        flash(f'Welcome back, {user.name.split()[0]}!', 'success')

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('main.dashboard_redirect'))

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out. See you on the trail!', 'info')
    return redirect(url_for('main.index'))