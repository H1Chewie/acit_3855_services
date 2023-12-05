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

def get_health_stats():
    logger.info("Getting health stats")
    try:
        with open(app_config['datastore']['filename'], 'r') as file:
            data = json.load(file)
        return data, 200
    except:
        return "Failed to retrieve stats", 400        


def health_service_status(service, url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            logger.info(f"Retrieved health status of {service}")
            return 'Running'
    except requests.RequestException as e:
        logger.error(f"Failed to connect to {service}: {e}")
    return 'Down'

def change_health_status():
    logger.info("Retrieving health status of all the services.")        
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    health_status = {
        'Receiver': health_service_status('Receiver', app_config['eventstore']['url'] + app_config['service']['receiver']),
        'Storage': health_service_status('Storage', app_config['eventstore']['url'] + app_config['service']['storage']),
        'Processing': health_service_status('Processing', app_config['eventstore']['url'] + app_config['service']['processing']),
        'Audit': health_service_status('Audit', app_config['eventstore']['url'] + app_config['service']['audit']),
        'last_update': current_datetime
    }
    
    with open(app_config['datastore']['filename'], 'w') as file:
        json.dump(health_status, file, indent=2)

    logger.info("Health status of all the services.")      
    return health_status, 200

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(change_health_status, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path="/health_check", strict_validation=True, validate_responses=True)
    
if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)