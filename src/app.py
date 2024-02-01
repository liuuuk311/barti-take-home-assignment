from datetime import time
from flask import Flask
from src.extensions import db
from src.endpoints import base
from src.models import Doctor, WorkingHours


def populate_db():
    doctor_strange = Doctor(name='Strange')
    db.session.add(doctor_strange)
    doctor_who = Doctor(name='Who')
    db.session.add(doctor_who)
    db.session.commit()
    for day in range(5): # 0 is Monday, 4 is Friday
        db.session.add(WorkingHours(doctor=doctor_strange, day_of_the_week=day, start_time=time(hour=9), end_time=time(hour=17)))
        db.session.add(WorkingHours(doctor=doctor_who, day_of_the_week=day, start_time=time(hour=8), end_time=time(hour=16)))
    db.session.commit()


def create_app(populate_db=True):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.init_app(app)
    # We are doing a create all here to set up all the tables. Because we are using an in memory sqllite db, each
    # restart wipes the db clean, but does have the advantage of not having to worry about schema migrations.
    with app.app_context():
        db.create_all()
        if populate_db:
            populate_db()

    app.register_blueprint(base)
    return app
