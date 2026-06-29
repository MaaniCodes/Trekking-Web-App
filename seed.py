from datetime import date, datetime
from extensions import db
from models import (
    User, Trek, Booking,
    ROLE_ADMIN, ROLE_STAFF, ROLE_TREKKER,
    TREK_PENDING, TREK_APPROVED, TREK_OPEN, TREK_CLOSED, TREK_COMPLETED,
    BOOKING_BOOKED, BOOKING_CANCELLED, BOOKING_COMPLETED,
    DIFF_EASY, DIFF_MODERATE, DIFF_HARD,
)


def seed_database():
    """Populate the database with initial demo data. Safe to call multiple times."""
    db.create_all()

    # Skip if already seeded
    if User.query.filter_by(email='admin@hikershub.com').first():
        print('[Seed] Database already seeded — skipping.')
        return

    print('[Seed] Creating demo data...')

    # ---- Admin ----
    admin = User(name='Maanvardhan Singh', email='admin@hikershub.com', role=ROLE_ADMIN)
    admin.set_password('Admin@123')
    db.session.add(admin)

    # ---- Staff ----
    staff1 = User(
        name='Meera Verma', email='meera.verma@example.com', role=ROLE_STAFF,
        phone='9876501234', city='Dehradun', is_staff_approved=True,
        bio='Certified mountain guide with 8 years of Himalayan experience. Specialises in winter and high-altitude routes.'
    )
    staff1.set_password('Staff@123')
    db.session.add(staff1)

    staff2 = User(
        name='Arjun Nair', email='arjun.nair@example.com', role=ROLE_STAFF,
        phone='9845067890', city='Manali', is_staff_approved=False,
        bio='Adventure enthusiast and trekking instructor from Himachal Pradesh.'
    )
    staff2.set_password('Staff@123')
    db.session.add(staff2)

    # ---- Trekkers ----
    trekker1 = User(
        name='Priya Sharma', email='priya.sharma@example.com', role=ROLE_TREKKER,
        phone='9900112233', city='Bengaluru',
        bio='Weekend hiker who chases sunrises above the treeline.'
    )
    trekker1.set_password('Trek@123')
    db.session.add(trekker1)

    trekker2 = User(
        name='Rahul Joshi', email='rahul.joshi@example.com', role=ROLE_TREKKER,
        phone='9711223344', city='Pune',
        bio='Completed 6 major Himalayan treks. Always looking for the next summit.'
    )
    trekker2.set_password('Trek@123')
    db.session.add(trekker2)

    trekker3 = User(
        name='Kavya Reddy', email='kavya.reddy@example.com', role=ROLE_TREKKER,
        phone='9988776655', city='Hyderabad',
        bio='Botanist and nature lover. Fascinated by alpine flora.'
    )
    trekker3.set_password('Trek@123')
    db.session.add(trekker3)

    db.session.flush()  # Get IDs before creating treks

    # ---- Treks ----
    trek1 = Trek(
        name='Kedarkantha Summit Trek',
        location='Sankri, Uttarakhand',
        description=(
            'Kedarkantha is one of India\'s finest winter treks, offering sweeping views of major Himalayan '
            'peaks including Swargarohini, Bandarpoonch, Kalanag, and the Gangotri group. The route winds '
            'through dense pine forests and pristine snow meadows, culminating in a dramatic summit at 12,500 ft. '
            'Perfect for trekkers seeking their first high-altitude winter experience.'
        ),
        difficulty=DIFF_HARD,
        duration_days=6,
        total_slots=30,
        available_slots=23,
        status=TREK_OPEN,
        price_per_person=8500,
        max_altitude='12,500 ft (3,810 m)',
        meeting_point='Dehradun ISBT, Gate 4',
        start_date=date(2025, 12, 18),
        end_date=date(2025, 12, 23),
        image_num=1,
        assigned_staff_id=staff1.id,
    )

    trek2 = Trek(
        name='Hampta Pass Crossing',
        location='Kullu, Himachal Pradesh',
        description=(
            'The Hampta Pass trek is a dramatic crossing from the lush Kullu valley to the stark, lunar landscape '
            'of the Lahaul valley. Crossing at 14,010 ft, trekkers experience a breathtaking transformation — from '
            'green alpine meadows and roaring streams to high-altitude desert and ancient moraines. '
            'One of the most scenic passes in the Western Himalayas.'
        ),
        difficulty=DIFF_MODERATE,
        duration_days=5,
        total_slots=25,
        available_slots=17,
        status=TREK_OPEN,
        price_per_person=6800,
        max_altitude='14,010 ft (4,270 m)',
        meeting_point='Manali Bus Stand, Himachal Tourism Counter',
        start_date=date(2025, 9, 10),
        end_date=date(2025, 9, 14),
        image_num=2,
        assigned_staff_id=staff1.id,
    )

    trek3 = Trek(
        name='Valley of Blooms Trek',
        location='Chamoli, Uttarakhand',
        description=(
            'Walk through an otherworldly valley carpeted in hundreds of species of wildflowers — from the iconic '
            'Brahmakamal to delicate blue poppies found nowhere else on earth. This short, accessible trek is a UNESCO '
            'World Heritage site and best visited between July and September. Great for beginners and nature enthusiasts.'
        ),
        difficulty=DIFF_EASY,
        duration_days=4,
        total_slots=40,
        available_slots=33,
        status=TREK_OPEN,
        price_per_person=4200,
        max_altitude='11,778 ft (3,589 m)',
        meeting_point='Govindghat, near Badrinath Highway',
        start_date=date(2025, 8, 5),
        end_date=date(2025, 8, 8),
        image_num=3,
        assigned_staff_id=None,
    )

    trek4 = Trek(
        name='Brahmatal Lake Ascent',
        location='Lohajung, Chamoli, Uttarakhand',
        description=(
            'Brahmatal offers a magnificent winter trek through oak and rhododendron forests to a frozen lake '
            'at 12,000 ft. Stunning views of Trishul and Nanda Ghunti peaks greet you at the top. '
            'A relatively offbeat route that remains uncrowded and pristine — ideal for intermediate trekkers.'
        ),
        difficulty=DIFF_MODERATE,
        duration_days=5,
        total_slots=20,
        available_slots=20,
        status=TREK_APPROVED,
        price_per_person=5800,
        max_altitude='12,200 ft (3,718 m)',
        meeting_point='Kathgodam Railway Station',
        start_date=date(2026, 1, 10),
        end_date=date(2026, 1, 14),
        image_num=4,
        assigned_staff_id=None,
    )

    trek5 = Trek(
        name='Chopta Ridge Walk',
        location='Rudraprayag, Uttarakhand',
        description=(
            'Called the "Switzerland of Uttarakhand," Chopta is a stunning meadow at 8,790 ft surrounded by '
            'oak, rhododendron, and deodar forests. This easy ridge walk leads to the ancient Tungnath temple '
            '— the highest Shiva shrine in the world — and continues to Chandrashila peak for panoramic views. '
            'Perfect for beginners and families.'
        ),
        difficulty=DIFF_EASY,
        duration_days=3,
        total_slots=35,
        available_slots=35,
        status=TREK_PENDING,
        price_per_person=3200,
        max_altitude='13,123 ft (3,999 m)',
        meeting_point='Rishikesh, Triveni Ghat Bus Stop',
        start_date=date(2025, 11, 1),
        end_date=date(2025, 11, 3),
        image_num=5,
        assigned_staff_id=None,
    )

    trek6 = Trek(
        name='Sandakphu Ridge Traverse',
        location='Darjeeling, West Bengal',
        description=(
            'Sandakphu is the highest peak in West Bengal and one of the few places on earth where you can see four '
            'of the world\'s five highest peaks — Everest, Kanchenjunga, Lhotse, and Makalu — simultaneously. '
            'The ridge traverse follows ancient trade routes used by Tibetan merchants, through Singalila National Park.'
        ),
        difficulty=DIFF_HARD,
        duration_days=7,
        total_slots=20,
        available_slots=20,
        status=TREK_COMPLETED,
        price_per_person=9500,
        max_altitude='11,930 ft (3,636 m)',
        meeting_point='New Jalpaiguri Railway Station',
        start_date=date(2025, 4, 10),
        end_date=date(2025, 4, 16),
        image_num=6,
        assigned_staff_id=staff1.id,
    )

    for t in [trek1, trek2, trek3, trek4, trek5, trek6]:
        db.session.add(t)

    db.session.flush()

    # ---- Bookings ----
    booking1 = Booking(
        user_id=trekker1.id, trek_id=trek1.id, status=BOOKING_BOOKED,
        emergency_contact='Raj Sharma – +91 9900112244',
        notes='Vegetarian meals please.',
    )
    booking2 = Booking(
        user_id=trekker1.id, trek_id=trek2.id, status=BOOKING_BOOKED,
        emergency_contact='Raj Sharma – +91 9900112244',
    )
    booking3 = Booking(
        user_id=trekker1.id, trek_id=trek6.id, status=BOOKING_COMPLETED,
        booking_date=datetime(2025, 4, 1),
        emergency_contact='Raj Sharma – +91 9900112244',
    )
    booking4 = Booking(
        user_id=trekker2.id, trek_id=trek1.id, status=BOOKING_BOOKED,
        emergency_contact='Meena Joshi – +91 9711223355',
    )
    booking5 = Booking(
        user_id=trekker3.id, trek_id=trek3.id, status=BOOKING_BOOKED,
        emergency_contact='Suresh Reddy – +91 9988776644',
        notes='Allergic to peanuts.',
    )
    booking6 = Booking(
        user_id=trekker2.id, trek_id=trek2.id, status=BOOKING_BOOKED,
        emergency_contact='Meena Joshi – +91 9711223355',
    )

    for b in [booking1, booking2, booking3, booking4, booking5, booking6]:
        db.session.add(b)

    db.session.commit()
    print('[Seed] ✓ All demo data created successfully.')
    print('[Seed]   Admin login  → admin@hikershub.com / Admin@123')
    print('[Seed]   Staff login  → meera.verma@example.com / Staff@123')
    print('[Seed]   Trekker login → priya.sharma@example.com / Trek@123')