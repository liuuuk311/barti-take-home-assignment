from datetime import timedelta
from flask import Blueprint, jsonify
from http import HTTPStatus
from src import errors
from src.extensions import db
from src.helpers import brute_force_approach, find_earliest_available_slot
from src.models import Appointment, Doctor, WorkingHours
from webargs import fields
from webargs.flaskparser import use_kwargs

base = Blueprint('/', __name__)


# Helpful documentation:
# https://webargs.readthedocs.io/en/latest/framework_support.html
# https://flask.palletsprojects.com/en/2.0.x/quickstart/#variable-rules


@base.route('/health', methods=['GET'])
def health_check():
    return {'status': 'OK'}


# create a decorator function that validates the doctor_id and returns a 404 if the doctor is not found
# https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/
def validate_doctor_id(f):
    def wrapper(doctor_id, *args, **kwargs):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), HTTPStatus.NOT_FOUND
        return f(doctor, *args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@base.route('/doctors/<int:doctor_id>/appointments', methods=['GET'])
@use_kwargs({
    'start_time': fields.DateTime(required=True), 
    'end_time': fields.DateTime(required=True)
}, location="querystring")
@validate_doctor_id
def get_appointments(doctor, start_time, end_time):
    """ Get all appointments for a doctor between a start and end time """

    # Edge cases (partial overlap):
    # - Appointments that begin before the start time and end inside the time frame
    # - Appointments that begin inside the time frame and end after the end time

    availabilities = (
        Appointment.query
        .filter_by(doctor_id=doctor.id)
        .filter(Appointment.start_time < end_time, Appointment.end_time > start_time)
        .all()
    )
    return jsonify([availability.to_dict() for availability in availabilities]), HTTPStatus.OK


@base.route('/doctors/<int:doctor_id>/appointments', methods=['POST'])
@use_kwargs({
    'appointment_starts_at': fields.DateTime(required=True), 
    'appointment_ends_at': fields.DateTime(required=True),
    'notes': fields.String(required=False)
}, location="json")
@validate_doctor_id
def create_appointment(doctor, appointment_starts_at, appointment_ends_at, notes=None):
    """ Create an appointment for a doctor between a start and end time, return error if there's a conflict """  
    
    # This is an assumption, but I think it's a reasonable one.
    if appointment_starts_at.date() != appointment_ends_at.date():
        return jsonify({'error': errors.CANNOT_CREATE_APPOINTMENT_ON_DIFFERENT_DAYS_ERROR}), HTTPStatus.BAD_REQUEST
    
    if appointment_starts_at >= appointment_ends_at:
        return jsonify({'error': errors.CANNOT_CREATE_APPOINTMENT_WRONG_TIME_ORDER_ERROR}), HTTPStatus.BAD_REQUEST

    # A conflit can happen in the following cases:
    # - New appointment inside an existing appointment (edge case new appointment starts and ends at the same time as an existing appointment)
    # - New appointment starts before an existing appointment and ends inside it
    # - New appointment starts inside an existing appointment and ends after it
    # - New appointment starts before an existing appointment and ends after it

    # Check if we are trying to create an appointment inside an existing appointment
    conflict = Appointment.query.filter_by(doctor_id=doctor.id).filter(
        Appointment.start_time < appointment_ends_at,
        Appointment.end_time > appointment_starts_at
    ).first()

    if conflict:
        return jsonify({'error': errors.CANNOT_CREATE_APPOINTMENT_CONFLIT_ERROR}), HTTPStatus.CONFLICT

    # Check if we are trying to create an appointment outside of working hours  
    working_hours = (
        WorkingHours.query
        .filter_by(doctor_id=doctor.id)
        .filter(
            WorkingHours.day_of_the_week == appointment_starts_at.weekday(),
        ).first()
    )
    if working_hours is None: # Doctor is not working on the day of the appointment
        return jsonify({'error': errors.CANNOT_CREATE_APPOINTMENT_OUTSIDE_WORKING_HOURS_ERROR}), HTTPStatus.BAD_REQUEST

    # Appointment is outside working hours if it starts before the start time or ends after the end time
    if appointment_starts_at.time() < working_hours.start_time or appointment_ends_at.time() > working_hours.end_time: 
        return jsonify({'error': errors.CANNOT_CREATE_APPOINTMENT_OUTSIDE_WORKING_HOURS_ERROR}), HTTPStatus.BAD_REQUEST
    
    new_appointment = Appointment(
        start_time=appointment_starts_at,
        end_time=appointment_ends_at,
        doctor_id=doctor.id,
        notes=notes
    )
    db.session.add(new_appointment)
    db.session.commit()
    return jsonify(new_appointment.to_dict()), HTTPStatus.CREATED


@base.route('/appointments/first_available', methods=['GET'])
@use_kwargs({
    'start_time': fields.DateTime(required=True),
    'appointment_length_minutes': fields.Int(load_default=30, validate=lambda x: 0 < x <= Appointment.MAX_APPOINMENT_LENGTH)  # Default to 30 minutes if not specified
}, location="querystring")
def get_first_available_appointment(start_time, appointment_length_minutes):
    doctors = Doctor.query.join(WorkingHours).all()  # Get all doctors that have working hours
    
    # earliest_available, earliest_available_doctor_id = brute_force_approach(doctors, start_time, appointment_length_minutes)
    earliest_available, earliest_available_doctor_id = find_earliest_available_slot(doctors, start_time, appointment_length_minutes)
                
    if earliest_available:
        return jsonify({
            'start_time': earliest_available.isoformat(), 
            'end_time': (earliest_available + timedelta(minutes=appointment_length_minutes)).isoformat(),
            'doctor_id': earliest_available_doctor_id
        })

    return jsonify({'error': errors.CANNOT_FIND_AVAILABLE_APPOINTMENT_ERROR}), HTTPStatus.NOT_FOUND
        