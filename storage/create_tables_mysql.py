import mysql.connector
db_conn = mysql.connector.connect(host="acit3855kafkazoo.eastus2.cloudapp.azure.com", user="user",
password="", database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
CREATE TABLE car_events
(id INT NOT NULL AUTO_INCREMENT,
license_id VARCHAR(110) NOT NULL,
hours_parked INTEGER NOT NULL,
cost INTEGER NOT NULL,
timestamp VARCHAR(250) NOT NULL,
date_created DATETIME NOT NULL,
trace_id VARCHAR(100) NOT NULL,
email VARCHAR(250) NOT NULL,
CONSTRAINT car_events_pk PRIMARY KEY (id))
''')

db_cursor.execute('''
CREATE TABLE bike_events
(id INT NOT NULL AUTO_INCREMENT,
bike_model VARCHAR(110) NOT NULL,
bike_id INTEGER NOT NULL,
hours_parked INTEGER NOT NULL,
timestamp VARCHAR(100) NOT NULL,
trace_id VARCHAR(100) NOT NULL,
date_created DATETIME NOT NULL,
email VARCHAR(250) NOT NULL,
cost INTEGER NOT NULL,
CONSTRAINT bike_events_pk PRIMARY KEY (id))
''')
db_conn.commit()
db_conn.close()
