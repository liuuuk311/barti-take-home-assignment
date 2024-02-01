import calendar

from src.extensions import db
from sqlalchemy import UniqueConstraint


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Maybe use UUID instead to avoid exposing the number of doctors and possibile enumeration attacks
    name = db.Column(db.Text, nullable=False)

    working_hours = db.relationship('WorkingHours', backref='doctor', lazy=True)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

    def __repr__(self):
        return f"Doctor('{self.name}')"
    

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


class WorkingHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_of_the_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)

    __table_args__ = (UniqueConstraint('doctor_id', 'day_of_the_week', name='unique_doctor_working_hour_per_day'),)

    def __repr__(self):
        return f"WorkingHours('{self.day_of_the_week}', '{self.start_time}', '{self.end_time}')"

    def to_dict(self):
        return {
            'id': self.id, 
            'day': calendar.day_name[self.day_of_the_week], 
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(), 
        }
    

class Appointment(db.Model):
    MAX_APPOINMENT_LENGTH = 60 * 2 # 2 hours 

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, index=True)  # Indexing these columns will speed up queries to find conflict when using the brute force approach
    end_time = db.Column(db.DateTime, nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False, index=True)

    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"Appointment('{self.start_time}', '{self.end_time}')"

    def to_dict(self):
        return {
            'id': self.id, 
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
        }
