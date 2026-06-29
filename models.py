from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

# --- Role constants ---
ROLE_ADMIN = 'admin'
ROLE_STAFF = 'staff'
ROLE_TREKKER = 'trekker'

# --- Trek status constants ---
TREK_PENDING = 'Pending'
TREK_APPROVED = 'Approved'
TREK_OPEN = 'Open'
TREK_CLOSED = 'Closed'
TREK_COMPLETED = 'Completed'

TREK_STATUSES = [TREK_PENDING, TREK_APPROVED, TREK_OPEN, TREK_CLOSED, TREK_COMPLETED]

# --- Difficulty constants ---
DIFF_EASY = 'Easy'
DIFF_MODERATE = 'Moderate'
DIFF_HARD = 'Hard'

DIFFICULTIES = [DIFF_EASY, DIFF_MODERATE, DIFF_HARD]

# --- Booking status constants ---
BOOKING_BOOKED = 'Booked'
BOOKING_CANCELLED = 'Cancelled'
BOOKING_COMPLETED = 'Completed'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_TREKKER)

    # Profile fields
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    # Access control
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    is_staff_approved = db.Column(db.Boolean, default=False, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship(
        'Booking', back_populates='user', lazy='dynamic', foreign_keys='Booking.user_id'
    )
    assigned_treks = db.relationship(
        'Trek', back_populates='assigned_staff', foreign_keys='Trek.assigned_staff_id', lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN

    @property
    def is_staff(self):
        return self.role == ROLE_STAFF

    @property
    def is_trekker(self):
        return self.role == ROLE_TREKKER

    @property
    def display_status(self):
        if self.is_blacklisted:
            return 'Blacklisted'
        if self.role == ROLE_STAFF:
            return 'Approved' if self.is_staff_approved else 'Pending Approval'
        return 'Active'

    def __repr__(self):
        return f'<User {self.email} [{self.role}]>'


class Trek(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    location = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), nullable=False, default=DIFF_MODERATE)
    duration_days = db.Column(db.Integer, nullable=False, default=3)
    total_slots = db.Column(db.Integer, nullable=False, default=20)
    available_slots = db.Column(db.Integer, nullable=False, default=20)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default=TREK_PENDING)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    price_per_person = db.Column(db.Float, nullable=False, default=0.0)
    max_altitude = db.Column(db.String(60), nullable=True)
    meeting_point = db.Column(db.String(200), nullable=True)
    image_num = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_staff = db.relationship(
        'User', back_populates='assigned_treks', foreign_keys=[assigned_staff_id]
    )
    bookings = db.relationship(
        'Booking', back_populates='trek', lazy='dynamic', foreign_keys='Booking.trek_id'
    )

    @property
    def is_bookable(self):
        return self.status == TREK_OPEN and self.available_slots > 0

    @property
    def booked_count(self):
        return self.bookings.filter_by(status=BOOKING_BOOKED).count()

    @property
    def occupancy_pct(self):
        if self.total_slots == 0:
            return 0
        return int((self.booked_count / self.total_slots) * 100)

    def __repr__(self):
        return f'<Trek "{self.name}" [{self.status}]>'


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False, index=True)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default=BOOKING_BOOKED)
    emergency_contact = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='bookings', foreign_keys=[user_id])
    trek = db.relationship('Trek', back_populates='bookings', foreign_keys=[trek_id])

    def __repr__(self):
        return f'<Booking user={self.user_id} trek={self.trek_id} [{self.status}]>'