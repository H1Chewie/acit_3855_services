from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class CarEvent(Base):
    """ Car Parking Ticket """

    __tablename__ = "car_events"
    id = Column(Integer, primary_key=True)
    license_id = Column(String(100), nullable=False)
    hours_parked = Column(Integer, nullable=False)
    timestamp = Column(String(250), nullable=False)
    cost = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(100), nullable=False)
    email = Column(String(250), nullable=False)

    def __init__(self, license_id, hours_parked, timestamp, cost, trace_id, email):
        """ Initializes a parking ticket for cars """
        self.license_id = license_id
        self.hours_parked = hours_parked
        self.timestamp = timestamp
        self.cost = cost
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id
        self.email = email

    def to_dict(self):
        """ Dictionary Representation of the parking ticket """
        dict = {}
        dict['id'] = self.id
        dict['license_id'] = self.license_id
        dict['hours_parked'] = self.hours_parked
        dict['cost'] = self.cost
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id
        dict['email'] = self.email

        return dict
