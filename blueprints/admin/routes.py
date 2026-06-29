from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from blueprints.admin import admin_bp
from blueprints.admin.forms import TrekForm
from extensions import db
from models import (
    User, Trek, Booking,
    ROLE_ADMIN, ROLE_STAFF, ROLE_TREKKER,
    TREK_OPEN, TREK_COMPLETED,
    BOOKING_BOOKED, BOOKING_COMPLETED,
)
from utils import admin_required


# --- Dashboard ---

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_treks': Trek.query.count(),
        'open_treks': Trek.query.filter_by(status=TREK_OPEN).count(),
        'total_trekkers': User.query.filter_by(role=ROLE_TREKKER).count(),
        'total_staff': User.query.filter_by(role=ROLE_STAFF).count(),
        'pending_staff': User.query.filter_by(role=ROLE_STAFF, is_staff_approved=False, is_blacklisted=False).count(),
        'total_bookings': Booking.query.count(),
        'active_bookings': Booking.query.filter_by(status=BOOKING_BOOKED).count(),
        'pending_treks': Trek.query.filter_by(status='Pending').count(),
    }
    recent_treks = Trek.query.order_by(Trek.created_at.desc()).limit(8).all()
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    return render_template(
        'admin/dashboard.html', stats=stats,
        recent_treks=recent_treks, recent_bookings=recent_bookings
    )


# --- Trek Management ---

@admin_bp.route('/treks')
@login_required
@admin_required
def treks_list():
    q = request.args.get('q', '').strip()
    query = Trek.query
    if q:
        query = query.filter(
            db.or_(
                Trek.name.ilike(f'%{q}%'),
                Trek.location.ilike(f'%{q}%'),
                Trek.id == (int(q) if q.isdigit() else -1),
            )
        )
    treks = query.order_by(Trek.created_at.desc()).all()
    approved_staff = User.query.filter_by(role=ROLE_STAFF, is_staff_approved=True, is_blacklisted=False).all()
    return render_template('admin/treks.html', treks=treks, q=q, approved_staff=approved_staff)


@admin_bp.route('/treks/new', methods=['GET', 'POST'])
@login_required
@admin_required
def trek_new():
    form = TrekForm()
    # Populate staff dropdown
    staff_list = User.query.filter_by(role=ROLE_STAFF, is_staff_approved=True, is_blacklisted=False).all()
    form.assign_staff.choices = [(0, '— No guide assigned yet —')] + [(s.id, s.name) for s in staff_list]

    if form.validate_on_submit():
        trek = Trek(
            name=form.name.data.strip(),
            location=form.location.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            difficulty=form.difficulty.data,
            duration_days=form.duration_days.data,
            total_slots=form.total_slots.data,
            available_slots=form.available_slots.data,
            price_per_person=form.price_per_person.data,
            max_altitude=form.max_altitude.data.strip() if form.max_altitude.data else None,
            meeting_point=form.meeting_point.data.strip() if form.meeting_point.data else None,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data,
            assigned_staff_id=form.assign_staff.data if form.assign_staff.data else None,
            image_num=form.image_num.data or 1,
        )
        db.session.add(trek)
        db.session.commit()
        flash(f'Trek "{trek.name}" created successfully!', 'success')
        return redirect(url_for('admin.treks_list'))

    return render_template('admin/trek_form.html', form=form, trek=None, title='Add New Trek')


@admin_bp.route('/treks/<int:trek_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def trek_edit(trek_id):
    trek = db.get_or_404(Trek, trek_id)
    form = TrekForm(obj=trek)

    staff_list = User.query.filter_by(role=ROLE_STAFF, is_staff_approved=True, is_blacklisted=False).all()
    form.assign_staff.choices = [(0, '— No guide assigned —')] + [(s.id, s.name) for s in staff_list]

    if request.method == 'GET':
        form.assign_staff.data = trek.assigned_staff_id or 0

    if form.validate_on_submit():
        trek.name = form.name.data.strip()
        trek.location = form.location.data.strip()
        trek.description = form.description.data.strip() if form.description.data else None
        trek.difficulty = form.difficulty.data
        trek.duration_days = form.duration_days.data
        trek.total_slots = form.total_slots.data
        trek.available_slots = form.available_slots.data
        trek.price_per_person = form.price_per_person.data
        trek.max_altitude = form.max_altitude.data.strip() if form.max_altitude.data else None
        trek.meeting_point = form.meeting_point.data.strip() if form.meeting_point.data else None
        trek.start_date = form.start_date.data
        trek.end_date = form.end_date.data
        trek.status = form.status.data
        trek.assigned_staff_id = form.assign_staff.data if form.assign_staff.data else None
        trek.image_num = form.image_num.data or 1
        db.session.commit()
        flash(f'Trek "{trek.name}" updated.', 'success')
        return redirect(url_for('admin.treks_list'))

    return render_template('admin/trek_form.html', form=form, trek=trek, title='Edit Trek')


@admin_bp.route('/treks/<int:trek_id>/delete', methods=['POST'])
@login_required
@admin_required
def trek_delete(trek_id):
    trek = db.get_or_404(Trek, trek_id)
    name = trek.name
    # Remove associated bookings first
    Booking.query.filter_by(trek_id=trek_id).delete()
    db.session.delete(trek)
    db.session.commit()
    flash(f'Trek "{name}" and all associated bookings have been removed.', 'warning')
    return redirect(url_for('admin.treks_list'))


@admin_bp.route('/treks/<int:trek_id>/assign', methods=['POST'])
@login_required
@admin_required
def trek_assign_staff(trek_id):
    trek = db.get_or_404(Trek, trek_id)
    staff_id = request.form.get('staff_id', type=int)
    if staff_id:
        staff = db.session.get(User, staff_id)
        if staff and staff.role == ROLE_STAFF and staff.is_staff_approved:
            trek.assigned_staff_id = staff_id
            db.session.commit()
            flash(f'{staff.name} assigned to "{trek.name}".', 'success')
        else:
            flash('Invalid staff selection.', 'danger')
    else:
        trek.assigned_staff_id = None
        db.session.commit()
        flash('Staff assignment removed from this trek.', 'info')
    return redirect(url_for('admin.treks_list'))


# --- Staff Management ---

@admin_bp.route('/staff')
@login_required
@admin_required
def staff_list():
    q = request.args.get('q', '').strip()
    query = User.query.filter_by(role=ROLE_STAFF)
    if q:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{q}%'),
                User.email.ilike(f'%{q}%'),
                User.id == (int(q) if q.isdigit() else -1),
            )
        )
    staff = query.order_by(User.created_at.desc()).all()
    return render_template('admin/staff_list.html', staff=staff, q=q)


@admin_bp.route('/staff/<int:user_id>/approve', methods=['POST'])
@login_required
@admin_required
def staff_approve(user_id):
    user = db.get_or_404(User, user_id)
    if user.role != ROLE_STAFF:
        abort(400)
    user.is_staff_approved = True
    user.is_blacklisted = False
    db.session.commit()
    flash(f'{user.name}\'s guide account has been approved!', 'success')
    return redirect(url_for('admin.staff_list'))


@admin_bp.route('/staff/<int:user_id>/blacklist', methods=['POST'])
@login_required
@admin_required
def staff_toggle_blacklist(user_id):
    user = db.get_or_404(User, user_id)
    if user.role != ROLE_STAFF:
        abort(400)
    user.is_blacklisted = not user.is_blacklisted
    if user.is_blacklisted:
        user.is_staff_approved = False
    db.session.commit()
    action = 'blacklisted' if user.is_blacklisted else 'reinstated'
    flash(f'{user.name} has been {action}.', 'warning' if user.is_blacklisted else 'success')
    return redirect(url_for('admin.staff_list'))


# --- User (Trekker) Management ---

@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    q = request.args.get('q', '').strip()
    query = User.query.filter_by(role=ROLE_TREKKER)
    if q:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{q}%'),
                User.email.ilike(f'%{q}%'),
                User.id == (int(q) if q.isdigit() else -1),
            )
        )
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users_list.html', users=users, q=q)


@admin_bp.route('/users/<int:user_id>/blacklist', methods=['POST'])
@login_required
@admin_required
def user_toggle_blacklist(user_id):
    user = db.get_or_404(User, user_id)
    if user.role != ROLE_TREKKER:
        abort(400)
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    action = 'blacklisted' if user.is_blacklisted else 'reinstated'
    flash(f'{user.name} has been {action}.', 'warning' if user.is_blacklisted else 'success')
    return redirect(url_for('admin.users_list'))


# --- Bookings Overview ---

@admin_bp.route('/bookings')
@login_required
@admin_required
def bookings_list():
    status_filter = request.args.get('status', '').strip()
    q = request.args.get('q', '').strip()
    query = Booking.query.join(Trek).join(User, Booking.user_id == User.id)
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    if q:
        query = query.filter(
            db.or_(User.name.ilike(f'%{q}%'), Trek.name.ilike(f'%{q}%'))
        )
    bookings = query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings, status_filter=status_filter, q=q)