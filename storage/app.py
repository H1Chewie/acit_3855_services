import json
import connexion
from connexion import NoContent
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from base import Base
from bike_parking_ticket import BikeEvent
from car_parking_ticket import CarEvent
import yaml
import logging.config
import logging
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import time
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

# DB_ENGINE = create_engine("sqlite:///tickets.sqlite")
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File %s" % log_conf_file )

DB_ENGINE = create_engine(
    f'mysql+pymysql://{app_config["datastore"]["user"]}:{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}')


Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logging.info(
    f"Connecting to MySQL database on {app_config['datastore']['hostname']}:{app_config['datastore']['port']}")

def get_parked_cars(start_timestamp, end_timestamp):
    """ Gets parked cars after the timestamp """
    
    session = DB_SESSION()

    start_timestamp_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    cars = session.query(CarEvent).filter(and_(CarEvent.date_created >= start_timestamp_datetime, CarEvent.date_created < end_timestamp_datetime))
    results_list = [car.to_dict() for car in cars]
    session.close()
    logger.info("Query for parked cars after%s returns %d results" % (start_timestamp, len(results_list)))
    return results_list, 200

def get_parked_bikes(start_timestamp, end_timestamp):
    """ Gets parked bikes after the timestamp """
    
    session = DB_SESSION()
    start_timestamp_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    bikes = session.query(BikeEvent).filter(
        and_(BikeEvent.date_created >= start_timestamp_datetime,
        BikeEvent.date_created < end_timestamp_datetime))
    results_list = [bike.to_dict() for bike in bikes]
    session.close()
    logger.info("Query for parked bikes after %s returns %d results" % (start_timestamp, len(results_list)))
    return results_list, 200

def process_messages():
    """ Process event messages """

    max_retries = app_config["events"]["max_retries"]
    retry_interval = app_config["events"]["retry_interval"]
    current_retry = 0
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                                app_config["events"]["port"])
    while current_retry < max_retries: 
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            logger.info(f"successfully connected to Kafka.")
            break
        except Exception as e:
            logger.error(f"Failed to connect to Kafka. Retrying ... Retry Count: {current_retry + 1}")
            time.sleep(retry_interval)
            current_retry += 1

    # Create a consumer group, read only new messages (OffsetType.LATEST)
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                          reset_offset_on_start=False,
                                          auto_offset_reset=OffsetType.LATEST)
    
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "cpt":
            # Store the car parking ticket to the DB
            logger.info("Processing Event1")
            session = DB_SESSION()

            logger.info(f"cpt Data: {payload}")

            car_event = CarEvent(
                payload['license_id'],
                payload['hours_parked'],
                payload['timestamp'],
                payload['cost'],
                payload['trace_id'],
                payload['email']
            )
            session.add(car_event)
            session.commit()
            session.close()  
        
        elif msg["type"] == "bpt":
        # Store the bike parking ticket  to the DB
            try:
                session = DB_SESSION()
        
                bike_event = BikeEvent(
                    payload['bike_model'],
                    payload['bike_id'],
                    payload['hours_parked'],
                    payload['timestamp'],
                    payload['trace_id'],
                    payload['email'],
                    payload['cost']
                )
                print(bike_event)
                session.add(bike_event)
                print("added")
                session.commit()
                print("committed")
                session.close()
            except Exception as e:
                print(e)
        # Commit the new message as being read
        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    

    #create a thread
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
