from flask import render_template
from flask_login import login_required, current_user
from . import staff_bp
from extensions import db
from models import Trek, Booking, BOOKING_BOOKED
from utils import staff_required


@staff_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    # Only treks assigned to this staff member
    assigned_treks = Trek.query.filter_by(
        assigned_staff_id=current_user.id
    ).order_by(Trek.start_date).all()

    # Only bookings for those assigned treks
    assigned_trek_ids = [t.id for t in assigned_treks]
    bookings = Booking.query.filter(
        Booking.trek_id.in_(assigned_trek_ids)
    ).order_by(Booking.booking_date.desc()).all() if assigned_trek_ids else []

    stats = {
        'total_treks': len(assigned_treks),
        'total_bookings': len(bookings),
        'active_bookings': sum(1 for b in bookings if b.status == BOOKING_BOOKED),
    }

    return render_template(
        'staff/dashboard.html',
        treks=assigned_treks,
        bookings=bookings,
        stats=stats,
    )