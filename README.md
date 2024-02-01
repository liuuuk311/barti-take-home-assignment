## Setup
1. After cloning this repository, cd into it.
2. Set up virtual environment via ```python3 -m venv env``` 
3. Activate the virtual environment via ```source env/bin/activate```
4. If it's properly set up, ```which python``` should point to a python under api-skeleton/env.
5. Install dependencies via ```pip install -r requirements.txt```

## Starting local flask server
Under api-skeleton/src, run ```flask run --host=0.0.0.0 -p 8000```

By default, Flask runs with port 5000, but some MacOS services now listen on that port.

## Running unit tests
All the tests can be run via ```pytest``` under api-skeleton directory.

## Code Structure
This is meant to be barebones.

* src/app.py contains the code for setting up the flask app.
* src/endpoints.py contains all the code for enpoints.
* src/models.py contains all the database model definitions.
* src/extensions.py sets up the extensions (https://flask.palletsprojects.com/en/2.0.x/extensions/)

## Requirements

- [x] Implement a model to represent an appointment with one of two doctors (Strange, Who). Appointments can be arbitrary length i.e. 20 mins, 45 mins, 60 mins
- [x] Implement a model to represent the working hours of each doctor (9 AM to 5 PM, M-F for Strange, 8 AM to 4 PM M-F for Who). You can assume working hours are the same every week. i.e. The schedule is the same each week.
- [x] Implement an API to create an appointment, rejecting it if there's a conflict.
- [x] Implement an API to get all appointments within a time window for a specified doctor.
- [x] Implement an API to get the first available appointment after a specified time. i.e. I'm a patient and I'm looking for the first available appointment
- [x] Tests
- [x] Doc

## Assumptions

To ensure a quick delivery of the take home assignments here are some assumptions that were made.
- We are not concerned with possible enumeration attacks. So, `Doctor.id` can be just an integer. 
- The application only handles a single time zone. So, all timestamps and dates are time zone naive.
- The application does not take into consideration public holidays, it only relies on the doctor's working hours.
- The maximum appointment duration is 2 hours, this limit is shared between all doctors, in the future we might want to loose this constraint and let each doctor customize it.
- When getting the appointments for a doctor, the API returns all the appointments that overlap with the given time window, even if they start before the window or end after it (partial overlap).

## One solution two approaches

The provided code implements two distinct approaches to find the first available appointment slot for a set of doctors, given a start time and appointment length. The first approach is a brute force approach that iterates through each doctor, checks their working hours against the given start time, and then sequentially checks for appointment conflicts within a predefined look-ahead period. The second approach pre-generates potential available slots for each doctor based on their working hours, filters out slots that conflict with existing appointments, and then uses a heap to efficiently find the earliest available slot across all doctors.

