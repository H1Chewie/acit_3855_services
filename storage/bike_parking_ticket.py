from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class BikeEvent(Base):
    """ Bike Parking Ticket """

    __tablename__ = "bike_events"
    id = Column(Integer, primary_key=True)
    bike_model = Column(String(100), nullable=False)
    bike_id = Column(Integer, nullable=False)
    hours_parked = Column(Integer, nullable=False)
    timestamp = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(100), nullable=False)
    email = Column(String(250), nullable=False)
    cost = Column(Integer, nullable=False)

    def __init__(self, bike_model, bike_id, hours_parked, timestamp, trace_id, email, cost):
        """ Initializes a parking ticket for cars """
        self.bike_model = bike_model
        self.hours_parked = hours_parked
        self.bike_id = bike_id
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id
        self.email = email
        self.cost = cost

    def to_dict(self):
        """ Dictionary Representation of the parking ticket """
        dict = {}
        dict['id'] = self.id
        dict['bike_model'] = self.bike_model
        dict['bike_id'] = self.bike_id
        dict['hours_parked'] = self.hours_parked
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id
        dict['email'] = self.email
        dict['cost'] = self.cost

        return dict