import json
import connexion
from connexion import NoContent
from apscheduler.schedulers.background import BackgroundScheduler
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import json
import connexion
from connexion import NoContent
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import yaml
import logging.config
import logging
from flask_cors import CORS, cross_origin
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File %s" % log_conf_file )

def health_status():
    logger.info("Service is running")
    return 200

# Function to get car parking ticket from history
def get_parked_car(index):
    """ Get Car Parking Ticket from History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving car parking ticket at index %d" % index)
    msg_count = 0
    
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'cpt':
                if msg_count == index:
                    return {'message': msg}, 200
                else:
                    msg_count += 1
    except:
        logger.error("No more messages found")
        
    logger.error("Could not find car parking ticket at index %d" % index)
    return {"message": "Not Found"}, 404

# Function to get bike parking ticket from history
def get_parked_bike(index):
    """ Get Bike Parking Ticket from History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving bike parking ticket at index %d" % index)
    
    msg_count = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # Assuming the index is a property in the message
            if msg['type'] == 'bpt':
                if msg_count == index:
                    return {'message': msg}, 200
                else:
                    msg_count += 1
    except:
        logger.error("No more messages found")
        
    logger.error("Could not find bike parking ticket at index %d" % index)
    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ and os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path="/audit_log", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110, use_reloader=False)