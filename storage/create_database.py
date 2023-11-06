import sqlite3

conn = sqlite3.connect('tickets.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE car_events
          (id INTEGER PRIMARY KEY ASC,
          license_id VARCHAR(110) NOT NULL,
          hours_parked INTEGER NOT NULL,
          cost INTEGER NOT NULL,
          timestamp STRING NOT NULL,
          date_created VARCHAR(100) NOT NULL,
          trace_id STRING NOT NULL,
          email STRING NOT NULL)
          ''')

c.execute('''
          CREATE TABLE bike_events
          (id INTEGER PRIMARY KEY ASC,
          bike_model VARCHAR(110) NOT NULL,
          bike_id INTEGER NOT NULL,
          hours_parked INTEGER NOT NULL,
          timestamp STRING NOT NULL,
          date_created VARCHAR(100) NOT NULL,
          trace_id STRING NOT NULL,
          cost INTEGER NOT NULL,
          email STRING NOT NULL)
          ''')

conn.commit()
conn.close()
