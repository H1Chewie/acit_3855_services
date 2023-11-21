import json
import connexion
from connexion import NoContent
from datetime import datetime
import requests
import yaml
import logging
import logging.config
import uuid
from pykafka import KafkaClient
import time

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

max_retries = app_config["events"]["max_retries"]
retry_interval = app_config["events"]["retry_interval"]
current_retry = 0
hostname = "%s:%d" % (app_config["events"]["hostname"],
                            app_config["events"]["port"])
while current_retry < max_retries:
    logger.info("attempting connection")
    try:
        print(hostname)
        print(app_config['events']['topic'])
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config['events']['topic'])]
        logger.inf(f"Successfully connected to Kafka")
        producer = topic.get_sync_producer()
        break
    except Exception as e:
        print(e)
        logger.error(f"Failed to connect to Kafka. Retrying ... Retry Count: {current_retry + 1}")
        time.sleep(retry_interval)
        current_retry += 1

def report_car_parking_ticket(body):
    """ Receives a car parking ticket"""

    body['trace_id'] = str(uuid.uuid4()) #generates a unique trace ID
    logger.info(f"Received event car_parking_ticket request with a trace id of {body['trace_id']} ")

    if producer is None:
        return NoContent, 500
    msg = {
        "type": "cpt",
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event car_parking_ticket request with a trace id of {body['trace_id']} ")

    return NoContent, 201

def report_bike_parking_ticket(body):
    """ Receives a bike parking ticket """
    
    body['trace_id'] = str(uuid.uuid4())
    logger.info(f"Received event bike_parking_ticket request with a trace if of {body['trace_id']}")

    if producer is None:
        return NoContent, 500

    msg = {
        "type": "bpt",
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event car_parking_ticket request with a trace id of {body['trace_id']} ")
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yaml', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)