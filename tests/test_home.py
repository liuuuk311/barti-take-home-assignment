from http import HTTPStatus

from src.errors import CANNOT_CREATE_APPOINTMENT_CONFLIT_ERROR, CANNOT_CREATE_APPOINTMENT_ON_DIFFERENT_DAYS_ERROR, CANNOT_CREATE_APPOINTMENT_OUTSIDE_WORKING_HOURS_ERROR, CANNOT_CREATE_APPOINTMENT_WRONG_TIME_ORDER_ERROR


# Test get_appointments endpoint, when there are no appointments
def test_get_appointments_no_appointments(client, doctor_strange, dr_strange_working_hours):
    response = client.get(f'/doctors/{doctor_strange.id}/appointments?start_time=2020-01-01T00:00:00&end_time=2020-01-01T23:59:59')
    assert response.status_code == HTTPStatus.OK
    assert response.json == []


# Test get_appointments endpoint, when there are appointments
def test_get_appointments_with_appointments(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/doctors/{doctor_strange.id}/appointments?start_time=2024-01-01T00:00:00&end_time=2024-01-01T23:59:59')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
    assert response.json[0].get('start_time') == '2024-01-01T09:00:00'
    assert response.json[0].get('end_time') == '2024-01-01T10:00:00'


# Test get_appointments endpoint, when there are appointments but the appoinment starts before the window and ends inside it
def test_get_appointments_with_appointments_before_the_window(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/doctors/{doctor_strange.id}/appointments?start_time=2024-01-01T09:30:00&end_time=2024-01-01T10:30:00')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
    assert response.json[0].get('start_time') == '2024-01-01T09:00:00'
    assert response.json[0].get('end_time') == '2024-01-01T10:00:00'


# Test get_appointments endpoint, when there are appointments but the appoinment starts inside the window and ends after it
def test_get_appointments_with_appointments_after_the_window(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/doctors/{doctor_strange.id}/appointments?start_time=2024-01-01T09:30:00&end_time=2024-01-01T09:45:00')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
    assert response.json[0].get('start_time') == '2024-01-01T09:00:00'
    assert response.json[0].get('end_time') == '2024-01-01T10:00:00'


# Test get_appointments endpoint for an appointment matching the exact query window
def test_get_appointments_exact_match_window(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/doctors/{doctor_strange.id}/appointments?start_time=2024-01-01T09:00:00&end_time=2024-01-01T10:00:00')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
    assert response.json[0].get('start_time') == '2024-01-01T09:00:00'
    assert response.json[0].get('end_time') == '2024-01-01T10:00:00'


# Test get_appointments endpoint, when there are appointments, but not for the doctor we are looking for
def test_get_appointments_with_appointments_wrong_doctor(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/doctors/2/appointments?start_time=2024-01-01T00:00:00&end_time=2024-01-01T23:59:59')
    assert response.status_code == HTTPStatus.NOT_FOUND


# Test get_appointments endpoint without the start_time parameter
def test_get_appointments_without_start_time(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/doctors/{doctor_strange.id}/appointments?end_time=2024-01-01T23:59:59')
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# Test get_appointments endpoint without the end_time parameter
def test_get_appointments_without_end_time(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/doctors/{doctor_strange.id}/appointments?start_time=2024-01-01T00:00:00')
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# Test get_appointments endpoint when there is one appointment that starts before the end_time parameter
def test_get_appointments_with_appointments_after_the_window(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/doctors/{doctor_strange.id}/appointments?start_time=2024-01-01T08:00:00&end_time=2024-01-01T08:30:00')
    assert response.status_code == HTTPStatus.OK
    assert response.json == []


# Test get_appointments endpoint when there is one appointment that ends after the start_time parameter
def test_get_appointments_with_appointments_before_the_window(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/doctors/{doctor_strange.id}/appointments?start_time=2024-01-01T10:30:00&end_time=2024-01-01T11:00:00')
    assert response.status_code == HTTPStatus.OK
    assert response.json == []


# Test create_appointment endpoint when there is no conflict
def test_create_appointment_no_conflict(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T10:30:00', 
        'appointment_ends_at': '2024-01-01T11:00:00',
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.CREATED
    assert response.json.get('start_time') == '2024-01-01T10:30:00'
    assert response.json.get('end_time') == '2024-01-01T11:00:00'


# Test create_appointment endpoint when there is a conflict, but the new appointment starts and ends at the same time as an existing appointment
def test_create_appointment_conflict_same_time(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T09:00:00', 
        'appointment_ends_at': '2024-01-01T10:00:00',
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json == {'error': CANNOT_CREATE_APPOINTMENT_CONFLIT_ERROR}

# Test create_appointment endpoint when there is a conflict, but the new appointment starts before an existing appointment and ends inside it
def test_create_appointment_conflict_before_and_inside(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T08:30:00', 
        'appointment_ends_at': '2024-01-01T09:30:00',
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json == {'error': CANNOT_CREATE_APPOINTMENT_CONFLIT_ERROR}


# Test create_appointment endpoint when there is a conflict, but the new appointment starts inside an existing appointment and ends after it
def test_create_appointment_conflict_inside_and_after(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T09:30:00', 
        'appointment_ends_at': '2024-01-01T10:30:00',
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json == {'error': CANNOT_CREATE_APPOINTMENT_CONFLIT_ERROR}


# Test create_appointment endpoint with new appoiment fully outside of working hours (before)
def test_create_appointment_outside_working_hours(client, doctor_strange, dr_strange_working_hours):
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T07:30:00', 
        'appointment_ends_at': '2024-01-01T08:30:00',
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {'error': CANNOT_CREATE_APPOINTMENT_OUTSIDE_WORKING_HOURS_ERROR}


# Test create_appointment endpoint with new appoiment fully outside of working hours (after)
def test_create_appointment_outside_working_hours_after(client, doctor_strange, dr_strange_working_hours):
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T17:30:00', 
        'appointment_ends_at': '2024-01-01T18:30:00',
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {'error': CANNOT_CREATE_APPOINTMENT_OUTSIDE_WORKING_HOURS_ERROR}


# Test create_appointment endpoint with new appoiment that starts inside working hours, but ends outside of it
def test_create_appointment_outside_working_hours_end(client, doctor_strange, dr_strange_working_hours):
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T16:30:00', 
        'appointment_ends_at': '2024-01-01T17:30:00',  # Outside working hours
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {'error': CANNOT_CREATE_APPOINTMENT_OUTSIDE_WORKING_HOURS_ERROR}

# Test create_appointment endpoint for back-to-back appointments
def test_create_appointment_back_to_back(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    payload = {
        'appointment_starts_at': '2024-01-01T10:00:00',
        'appointment_ends_at': '2024-01-01T10:30:00',
        'notes': 'Starts right after an existing appointment ends'
    }
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json=payload)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json.get('start_time') == '2024-01-01T10:00:00'


# Test create_appointment endpoint with new appoiment that starts before working hours, but ends inside of it
def test_create_appointment_outside_working_hours_start(client, doctor_strange, dr_strange_working_hours):
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T08:30:00',  # Outside working hours
        'appointment_ends_at': '2024-01-01T09:30:00', 
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {'error': CANNOT_CREATE_APPOINTMENT_OUTSIDE_WORKING_HOURS_ERROR}


# Test create_appointment endpoint for a non existing doctor
def test_create_appointment_non_existing_doctor(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.post(f'/doctors/999/appointments', json={
        'appointment_starts_at': '2024-01-01T10:30:00', 
        'appointment_ends_at': '2024-01-01T11:00:00',
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {'error': 'Doctor not found'}


# Test create_appoinment over different days
def test_create_appointment_over_different_days(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T10:30:00',  # Inside working hours
        'appointment_ends_at': '2024-01-02T11:00:00',  # Inside working hours, but different day
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {'error': CANNOT_CREATE_APPOINTMENT_ON_DIFFERENT_DAYS_ERROR}


# Test create_appointment twice should work the first time, but fail the second time
def test_create_appointment_twice(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    payload = {
        'appointment_starts_at': '2024-01-01T10:30:00', 
        'appointment_ends_at': '2024-01-01T11:00:00',
        'notes': 'test notes'
    }
    
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json=payload)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json.get('start_time') == '2024-01-01T10:30:00'
    assert response.json.get('end_time') == '2024-01-01T11:00:00'

    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json=payload)
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json == {'error': CANNOT_CREATE_APPOINTMENT_CONFLIT_ERROR}
    

# Test create_appointment with wrong time order
def test_create_appointment_wrong_time_order(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T11:00:00', 
        'appointment_ends_at': '2024-01-01T10:30:00',
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {'error': CANNOT_CREATE_APPOINTMENT_WRONG_TIME_ORDER_ERROR}


# Test create_appointment without notes
def test_create_appointment_without_notes(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T10:30:00', 
        'appointment_ends_at': '2024-01-01T11:00:00',
    })
    assert response.status_code == HTTPStatus.CREATED
    assert response.json.get('start_time') == '2024-01-01T10:30:00'
    assert response.json.get('end_time') == '2024-01-01T11:00:00'


# Test create_appointment and the get appointments for the doctors
def test_create_appointment_and_get_appointments(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/doctors/{doctor_strange.id}/appointments?start_time=2024-01-01T00:00:00&end_time=2024-01-01T23:59:59')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1

    response = client.post(f'/doctors/{doctor_strange.id}/appointments', json={
        'appointment_starts_at': '2024-01-01T10:30:00', 
        'appointment_ends_at': '2024-01-01T11:00:00',
        'notes': 'test notes'
    })
    assert response.status_code == HTTPStatus.CREATED
    assert response.json.get('start_time') == '2024-01-01T10:30:00'
    assert response.json.get('end_time') == '2024-01-01T11:00:00'

    response = client.get(f'/doctors/{doctor_strange.id}/appointments?start_time=2024-01-01T00:00:00&end_time=2024-01-01T23:59:59')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 2


# Test find first available appointment
def test_find_first_available_appointment(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/appointments/first_available?start_time=2024-01-01T00:00:00')
    assert response.status_code == HTTPStatus.OK
    assert response.json.get('start_time') == '2024-01-01T10:00:00' # Because the doctor start working at 9:00 but has an appointment until 10:00
    assert response.json.get('end_time') == '2024-01-01T10:30:00'
    assert response.json.get('doctor_id') == doctor_strange.id


# Test find first available appointment when there are no doctors
def test_find_first_available_appointment_no_doctors(client):
    response = client.get(f'/appointments/first_available?start_time=2024-01-01T00:00:00')
    assert response.status_code == HTTPStatus.NOT_FOUND


# Test find first available appointment when there are two doctors
def test_find_first_available_appointment_two_doctors(
    client, doctor_strange, doctor_who, dr_strange_working_hours, dr_who_working_hours, dr_strange_appointment, dr_who_appointment
):
    response = client.get(f'/appointments/first_available?start_time=2024-01-01T00:00:00')
    assert response.status_code == HTTPStatus.OK
    assert response.json.get('start_time') == '2024-01-01T08:00:00' # Because the doctor who working at 8:00 and has no appointments at that time
    assert response.json.get('end_time') == '2024-01-01T08:30:00'
    assert response.json.get('doctor_id') == doctor_who.id


# Test find first available appointment starting at 17:00
def test_find_first_available_appointment_starting_at_17(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/appointments/first_available?start_time=2024-01-01T17:00:00')
    assert response.status_code == HTTPStatus.OK
    assert response.json.get('start_time') == '2024-01-02T09:00:00' # Because the doctor signs off at 5PM and starts working at 9AM of the next day
    assert response.json.get('end_time') == '2024-01-02T09:30:00'
    assert response.json.get('doctor_id') == doctor_strange.id


# Test find first available appointment starting at 6:00
def test_find_first_available_appointment_starting_at_6(client, doctor_who, dr_who_working_hours, dr_who_appointment):
    response = client.get(f'/appointments/first_available?start_time=2024-01-01T06:00:00')
    assert response.status_code == HTTPStatus.OK
    assert response.json.get('start_time') == '2024-01-01T08:00:00' # Because the doctor starts working at 8AM
    assert response.json.get('end_time') == '2024-01-01T08:30:00'
    assert response.json.get('doctor_id') == doctor_who.id


# Test find first available appointment with a doctor full schedule
def test_find_first_available_appointment_full_schedule(client, doctor_strange, dr_strange_working_hours, dr_strange_month_full_of_appointments):
    response = client.get(f'/appointments/first_available?start_time=2024-01-01T00:00:00')
    assert response.status_code == HTTPStatus.NOT_FOUND  # Because the doctor has a full schedule for the next 30 days


# Test find first available appointment with a doctor full schedule, but only for 10 days
def test_find_first_available_appointment_10_days_schedule(client, doctor_strange, dr_strange_working_hours, dr_strange_10_days_appointments):
    response = client.get(f'/appointments/first_available?start_time=2024-01-01T00:00:00')
    assert response.status_code == HTTPStatus.OK
    assert response.json.get('start_time') == '2024-01-11T09:00:00' # Because the doctor has a full schedule for the next 10 days
    assert response.json.get('end_time') == '2024-01-11T09:30:00'
    assert response.json.get('doctor_id') == doctor_strange.id

# Test find first available appointment starting on a non working day
def test_find_first_available_appointment_starting_on_non_working_day(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/appointments/first_available?start_time=2024-01-06T00:00:00')
    assert response.status_code == HTTPStatus.OK
    assert response.json.get('start_time') == '2024-01-08T09:00:00' # Because the doctor starts working at 9AM on Monday
    assert response.json.get('end_time') == '2024-01-08T09:30:00'
    assert response.json.get('doctor_id') == doctor_strange.id


# Test find first available appointment with a custom appointment length
def test_find_first_available_appointment_custom_length(client, doctor_strange, dr_strange_working_hours, dr_strange_appointment):
    response = client.get(f'/appointments/first_available?start_time=2024-01-01T00:00:00&appointment_length_minutes=60')
    assert response.status_code == HTTPStatus.OK
    assert response.json.get('start_time') == '2024-01-01T10:00:00' # Because the doctor start working at 9:00 but has an appointment until 10:00
    assert response.json.get('end_time') == '2024-01-01T11:00:00'
    assert response.json.get('doctor_id') == doctor_strange.id