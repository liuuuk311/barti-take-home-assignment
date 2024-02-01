from datetime import datetime, timedelta
import heapq
from operator import and_, or_
from typing import Dict, List, Optional, Tuple

from src.models import Appointment, Doctor, WorkingHours


def brute_force_approach(doctors: List[Doctor], start_time: datetime, appointment_length_minutes: int) -> Tuple[Optional[datetime], Optional[int]]:
    earliest_available = None
    earliest_available_doctor = None

    for doctor in doctors:
        working_hours = {wh.day_of_the_week: wh for wh in doctor.working_hours}
        available_slot = find_first_available_slot(doctor, working_hours, start_time, appointment_length_minutes)
        
        if available_slot and (earliest_available is None or available_slot < earliest_available):
            earliest_available = available_slot
            earliest_available_doctor = doctor

    return earliest_available, earliest_available_doctor.id if earliest_available_doctor else None
    

def find_first_available_slot(
    doctor: Doctor, working_hours: Dict[int, WorkingHours], start_time: datetime, appointment_length_minutes: int, max_look_ahead_in_days: int = 30
    ):
    max_look_ahead = timedelta(days=max_look_ahead_in_days) 
    
    current_day, current_time = start_time.date(), start_time.time()
    while current_day - start_time.date() < max_look_ahead:
        if day_of_week := current_day.weekday() not in working_hours: # Move to the next day if the current day is not a working day
            current_day, current_time = next_working_day_start(working_hours, current_day)

        wh = working_hours[day_of_week]
        # Check if the current_time is within the working hours for the current day
        if wh.start_time <= current_time < wh.end_time:
            potential_start = datetime.combine(current_day, current_time)
            potential_end = potential_start + timedelta(minutes=appointment_length_minutes)
            
            # Ensure the potential end time does not exceed working hours
            if potential_end.time() > wh.end_time:
                continue # Discard this potential slot and move to the next one
            
            conflitcs = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                or_(
                    and_(Appointment.start_time <= potential_start, Appointment.end_time > potential_start),
                    and_(Appointment.start_time < potential_end, Appointment.end_time >= potential_end)
                )
            ).all()
            
            # If no conflicting appointments, this time slot is available
            if not conflitcs:
                return potential_start
        
        # Move to the next possible start time within the working day
        current_time = (datetime.combine(current_day, current_time) + timedelta(minutes=appointment_length_minutes)).time()
        # If current_time exceeds working hours or it's not a working day, move to the next working day
        if current_time >= wh.end_time or day_of_week not in working_hours:
            current_day, current_time = next_working_day_start(working_hours, current_day)


def next_working_day_start(working_hours: Dict[int, WorkingHours], current_day: datetime):
    current_day += timedelta(days=1)
    while current_day.weekday() not in working_hours:
        current_day += timedelta(days=1)
    return current_day, working_hours[current_day.weekday()].start_time


# ========== Alternative approach using a heap ==========

def find_earliest_available_slot(
    doctors: List[Doctor], start_time: datetime, appointment_length_minutes: int
) -> Tuple[Optional[datetime], Optional[int]]:
    potential_slots = []
    appointment_length = timedelta(minutes=appointment_length_minutes)

    for doctor in doctors:
        slots = generate_slots_for_doctor(doctor, start_time, appointment_length)
        for slot in slots:
            # Push the slot start time and doctor ID as a tuple into the heap
            heapq.heappush(potential_slots, (slot, doctor.id))

    if not potential_slots:
        return None, None
    
    earliest_slot, doctor_id = heapq.heappop(potential_slots)
    return earliest_slot, doctor_id


def generate_slots_for_doctor(
    doctor: Doctor, start_time: datetime, appointment_length: int, max_look_ahead_in_days: int = 30, increment_by_minutes: int = 15
):
    slots = []
    current_date = start_time.date()
    look_head_limit = current_date + timedelta(days=max_look_ahead_in_days)  # Arbitrary end date for searching

    working_hours_map = {wh.day_of_the_week: wh for wh in doctor.working_hours}
    # If start_time is after working hours, start checking from the next day
    if start_time.weekday() in working_hours_map and start_time.time() >= working_hours_map[start_time.weekday()].end_time:
        current_date, _ = next_working_day_start(working_hours_map, current_date)

    while current_date <= look_head_limit:
        working_hours = [wh for wh in doctor.working_hours if wh.day_of_the_week == current_date.weekday()]

        for wh in working_hours:
            current_slot_start = datetime.combine(current_date, wh.start_time)
            working_day_end = datetime.combine(current_date, wh.end_time)

            while current_slot_start + appointment_length <= working_day_end:
                slots.append(current_slot_start)
                current_slot_start += timedelta(minutes=increment_by_minutes)

        current_date += timedelta(days=1)

    # Remove slots that conflict with existing appointments
    slots = [slot for slot in slots if slot_fits_appointment(slot, appointment_length, doctor.appointments)]
    return slots


def slot_fits_appointment(slot_start: datetime, appointment_length: timedelta, appointments: List[Appointment]):
    slot_end = slot_start + appointment_length
    for appointment in appointments:
        if not (slot_end <= appointment.start_time or slot_start >= appointment.end_time):
            return False
    return True
