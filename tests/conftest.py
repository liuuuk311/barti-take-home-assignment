from datetime import time, datetime, timedelta
import pytest

from src.app import create_app


@pytest.fixture()
def app():
    app = create_app(populate_db=False)
    yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def db(app):
    with app.app_context():
        from src.extensions import db
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture
def doctor_strange(db):
    from src.models import Doctor
    doctor = Doctor(name='Strange')
    db.session.add(doctor)
    db.session.commit()
    return doctor


@pytest.fixture
def dr_strange_working_hours(db, doctor_strange):
    from src.models import WorkingHours
    working_hours = []
    for day in range(5): # 0 is Monday, 4 is Friday
        working_hours.append(WorkingHours(
            day_of_the_week=day,
            start_time=time(hour=9),
            end_time=time(hour=17),
            doctor_id=doctor_strange.id
        ))
    db.session.add_all(working_hours)
    db.session.commit()
    return working_hours


@pytest.fixture
def dr_strange_appointment(db, doctor_strange):
    from src.models import Appointment
    appointment = Appointment(
        start_time=datetime(year=2024, month=1, day=1, hour=9),
        end_time=datetime(year=2024, month=1, day=1, hour=10),
        doctor_id=doctor_strange.id
    )
    db.session.add(appointment)
    db.session.commit()
    return appointment


@pytest.fixture
def dr_strange_month_full_of_appointments(db, doctor_strange):
    """Create 30 appointments of 8 hours each for Dr Strange starting from 2024-01-01 09:00:00"""
    from src.models import Appointment
    appointments = []
    start_date = datetime(year=2024, month=1, day=1, hour=9)
    for day in range(31): # Create an appointment for each day at 9am for 8 hours
        appointments.append(Appointment(
            start_time=start_date + timedelta(days=day),
            end_time=start_date + timedelta(days=day, hours=8),
            doctor_id=doctor_strange.id
        ))
    db.session.add_all(appointments)
    db.session.commit()
    return appointments


@pytest.fixture
def dr_strange_10_days_appointments(db, doctor_strange):
    """Create 10 appointments of 8 hours each for Dr Strange starting from 2024-01-01 09:00:00"""
    from src.models import Appointment
    appointments = []
    start_date = datetime(year=2024, month=1, day=1, hour=9)
    for day in range(10):
        appointments.append(Appointment(
            start_time=start_date + timedelta(days=day),
            end_time=start_date + timedelta(days=day, hours=8),
            doctor_id=doctor_strange.id
        ))
    db.session.add_all(appointments)
    db.session.commit()
    return appointments

@pytest.fixture
def doctor_who(db):
    from src.models import Doctor
    doctor = Doctor(name='Who')
    db.session.add(doctor)
    db.session.commit()
    return doctor


@pytest.fixture
def dr_who_working_hours(db, doctor_who):
    from src.models import WorkingHours
    working_hours = []
    for day in range(5): # 0 is Monday, 4 is Friday
        working_hours.append(WorkingHours(
            day_of_the_week=day,
            start_time=time(hour=8),
            end_time=time(hour=16),
            doctor_id=doctor_who.id
        ))
    db.session.add_all(working_hours)
    db.session.commit()
    return working_hours


@pytest.fixture
def dr_who_appointment(db, doctor_who):
    from src.models import Appointment
    appointment = Appointment(
        start_time=datetime(year=2024, month=1, day=1, hour=9),
        end_time=datetime(year=2024, month=1, day=1, hour=10),
        doctor_id=doctor_who.id
    )
    db.session.add(appointment)
    db.session.commit()
    return appointment