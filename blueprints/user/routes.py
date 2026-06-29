from flask import render_template
from flask_login import login_required, current_user
from . import user_bp
from models import Booking

@user_bp.route('/dashboard')
@login_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('user/dashboard.html', bookings=bookings)