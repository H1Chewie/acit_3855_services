import json
import connexion
from connexion import NoContent
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import yaml
import logging.config
import logging

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 
                  'interval', 
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()

def populate_stats():
    logger.info("Start Periodic Processing")

    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            json_object = json.load(f)
            max_car_cost = json_object["max_car_cost"]
            num_car_parkings = json_object['num_car_parkings']
            num_bike_events = json_object['num_bike_events']
            max_bike_cost = json_object['max_bike_cost']

    except:
        json_object = {
        "num_car_parkings": 0,
        "max_car_cost": 0,
        "num_bike_events": 0,
        "max_bike_cost": 0,
        "last_updated": "2021-02-05T12:39:16Z"
        }
        with open(app_config['datastore']['filename'], 'w') as f:
            json.dump(json_object, f, indent=4)

    
    # timestamp = datetime.now()    
    current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    response_car = requests.get(app_config['eventstore']['url1'], params={"timestamp": json_object["last_updated"]})
    response_bike = requests.get(app_config['eventstore']['url2'], params={"timestamp": json_object["last_updated"]})


    if response_car.status_code == 200 and response_bike.status_code == 200:

        car_string = response_car.content.decode('utf-8')
        car_json = json.loads(car_string)
        bike_string = response_bike.content.decode('utf-8')
        bike_json = json.loads(bike_string)


        num_car_parkings += len(car_json)
        num_bike_events += len(bike_json)
        if car_json != []:
            max_car_cost_new = max((item["cost"] for item in car_json))
            max_car_cost = max(max_car_cost, max_car_cost_new)
        if bike_json != []:
            max_bike_cost_new = max((item["cost"] for item in bike_json))
            max_bike_cost = max(max_bike_cost, max_bike_cost_new)


        last_updated = current_datetime
        
        updated_stats = {
            "num_car_parkings": num_car_parkings,
            "max_car_cost": max_car_cost,
            "num_bike_events": num_bike_events,
            "max_bike_cost": max_bike_cost,
            "last_updated": last_updated
            }

        logger.info(f"Received {len(car_json)} car events and {len(bike_json)} bike events")

        with open(app_config['datastore']['filename'], 'w') as fs:
            json.dump(updated_stats, fs, indent=4)
        
        logger.debug(f"Updated Stats: {updated_stats}")
    
    else:
        logger.error(f"Failed to get events. Car Status: {response_car.status_code}, Bike Status: {response_bike.status_code}")

    
    logger.info("End Periodic Processing")

def get_stats():
    logger.info("get_stats request has started")

    try:
        with open(app_config['datastore']['filename'], 'r') as fs:
            json_object = json.load(fs)
        return_dict = {
            "num_car_parkings": json_object.get('num_car_parkings', 0),
            "max_car_cost": json_object.get('max_car_cost', 0),
            "num_bike_events": json_object.get('num_bike_events', 0),
            "max_bike_cost": json_object.get('max_bike_cost', 0)
        }
        logger.debug(return_dict)
        logger.info("get_stats request completed")
        return return_dict, 200
    except FileNotFoundError:
        logger.error("No statistics currently exist")
        return "Statistics do not exist", 404


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('parkingAPI.yaml', strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)