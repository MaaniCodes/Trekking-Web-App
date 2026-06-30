from flask import render_template, redirect, url_for, request, abort
from flask_login import current_user, login_required
from blueprints.main import main_bp
from extensions import db
from models import Trek, User, Booking, TREK_OPEN, ROLE_TREKKER, ROLE_STAFF, ROLE_ADMIN, BOOKING_BOOKED


@main_bp.route('/')
def index():
    # Featured open treks for the home page grid
    featured = Trek.query.filter_by(status=TREK_OPEN).order_by(Trek.start_date).limit(6).all()

    # Stats for the numbers banner
    stats = {
        'total_treks': Trek.query.count(),
        'open_treks': Trek.query.filter_by(status=TREK_OPEN).count(),
        'total_trekkers': User.query.filter_by(role=ROLE_TREKKER).count(),
        'total_bookings': Booking.query.count(),
    }
    return render_template('main/index.html', featured=featured, stats=stats)


@main_bp.route('/treks')
def browse_treks():
    q = request.args.get('q', '').strip()
    difficulty = request.args.get('difficulty', '').strip()
    location = request.args.get('location', '').strip()

    query = Trek.query.filter_by(status=TREK_OPEN)

    if q:
        query = query.filter(
            db.or_(Trek.name.ilike(f'%{q}%'), Trek.location.ilike(f'%{q}%'))
        )
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))

    treks = query.order_by(Trek.start_date).all()

    # Unique locations for the filter dropdown
    all_locations = [
        r[0] for r in db.session.query(Trek.location)
        .filter_by(status=TREK_OPEN).distinct().all()
    ]

    return render_template(
        'main/browse_treks.html',
        treks=treks,
        q=q,
        difficulty=difficulty,
        location=location,
        all_locations=all_locations,
    )


@main_bp.route('/treks/<int:trek_id>')
def trek_detail(trek_id):
    trek = db.get_or_404(Trek, trek_id)

    # Non-admin, non-staff users can only view Open treks
    if trek.status != TREK_OPEN:
        if not current_user.is_authenticated or current_user.role == ROLE_TREKKER:
            abort(404)

    already_booked = False
    if current_user.is_authenticated and current_user.is_trekker:
        already_booked = Booking.query.filter_by(
            user_id=current_user.id,
            trek_id=trek_id,
            status=BOOKING_BOOKED
        ).first() is not None

    return render_template('main/trek_detail.html', trek=trek, already_booked=already_booked)


@main_bp.route('/dashboard')
@login_required
def dashboard_redirect():
    """Post-login redirect: send each role to its own dashboard."""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    if current_user.is_staff:
        return redirect(url_for('staff.dashboard'))
    return redirect(url_for('user.dashboard'))