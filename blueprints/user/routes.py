from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import user_bp
from extensions import db
from models import Booking, Trek, BOOKING_BOOKED, TREK_OPEN
from utils import trekker_required


@user_bp.route('/dashboard')
@login_required
@trekker_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template('user/dashboard.html', bookings=bookings)


@user_bp.route('/book/<int:trek_id>', methods=['POST'])
@login_required
@trekker_required
def book_trek(trek_id):
    trek = db.get_or_404(Trek, trek_id)

    # Trek must be open
    if trek.status != TREK_OPEN:
        flash('This trek is not available for booking.', 'danger')
        return redirect(url_for('main.trek_detail', trek_id=trek_id))

    # Must have available slots
    if trek.available_slots <= 0:
        flash('Sorry, this trek is fully booked.', 'danger')
        return redirect(url_for('main.trek_detail', trek_id=trek_id))

    # Check if user already booked this trek
    existing = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek_id,
        status=BOOKING_BOOKED
    ).first()
    if existing:
        flash('You have already booked this trek.', 'warning')
        return redirect(url_for('main.trek_detail', trek_id=trek_id))

    # Create booking and decrement slot
    booking = Booking(
        user_id=current_user.id,
        trek_id=trek_id,
        status=BOOKING_BOOKED,
        emergency_contact=request.form.get('emergency_contact', '').strip() or None,
        notes=request.form.get('notes', '').strip() or None,
    )
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()

    flash(f'You have successfully booked "{trek.name}"! Check your dashboard for details.', 'success')
    return redirect(url_for('user.dashboard'))


@user_bp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
@trekker_required
def cancel_booking(booking_id):
    booking = db.get_or_404(Booking, booking_id)

    # Make sure the booking belongs to the current user
    if booking.user_id != current_user.id:
        flash('You are not authorised to cancel this booking.', 'danger')
        return redirect(url_for('user.dashboard'))

    if booking.status != BOOKING_BOOKED:
        flash('This booking cannot be cancelled.', 'warning')
        return redirect(url_for('user.dashboard'))

    # Cancel and free up the slot
    booking.status = 'Cancelled'
    booking.trek.available_slots += 1
    db.session.commit()

    flash(f'Your booking for "{booking.trek.name}" has been cancelled.', 'info')
    return redirect(url_for('user.dashboard'))