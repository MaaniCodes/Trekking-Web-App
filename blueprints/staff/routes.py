from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import staff_bp
from extensions import db
from models import Trek, Booking
from utils import staff_required

@staff_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    treks = Trek.query.all()
    bookings = Booking.query.all()
    return render_template('staff/dashboard.html', treks=treks, bookings=bookings)