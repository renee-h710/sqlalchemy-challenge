import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine(f"sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
keys = Base.classes.keys()
print(keys)
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def Homepage():
    """List all available api routes."""
    return (f"Available Routes: <br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/start<br/> "
    f"/api/v1.0/start/end <br/>")


@app.route("/api/v1.0/precipitation")
def precipitation():
    # print("Server received request for 'precipitation' page...")
    #Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    #Return the JSON representation of your dictionary.
    session = Session(engine)
    results = session.query(Measurement.date,Measurement.prcp).all()
    session.close

    all_dates = []
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict['Date'] = date
        prcp_dict['Prcp'] = prcp
        all_dates.append(prcp_dict)

    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'stations' page...")
    #Return a JSON list of stations from the dataset.

    session = Session(engine)
    results = session.query(Station.station,Station.name).all()

    stations = []
    for station,name in results:
            station_dict = {}
            station_dict['station'] = station
            station_dict['name'] = name
            stations.append(station_dict)


    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():

    #Query the dates and temperature observations of the most active station for the previous year of data.
    active_station = 'USC00519281'

    results = session.query(Measurement.station,Measurement.date,Measurement.tobs).all()
 
    all_dates = []
    for station,date,tobs in results:
        tobs_dict = {}
        
        if (station == active_station) and (date.startswith('2017')):
            tobs_dict['Date'] = date
            tobs_dict['Tobs'] = tobs
            all_dates.append(tobs_dict)


    #Return a JSON list of temperature observations (TOBS) for the previous year.
    print("Server received request for 'tobs' page...")
    return jsonify(all_dates)


#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
@app.route("/api/v1.0/<start>")
def start(start):
    print("Server received request for 'start' page...")
    startStr = start
    startDate= dt.datetime.strptime(startStr, "%Y-%m-%d").date()
   
    session = Session(engine)
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than or equal to the start date.
    results = session.query(Measurement.date,Measurement.tobs).all()
    session.close
    temps =[]
    date_dict = {}
    for date,tobs in results:

        newDate= dt.datetime.strptime(date, "%Y-%m-%d").date()
        if newDate >= startDate:
            temps.append(tobs)
    
    date_dict['TMIN'] = np.min(temps)
    date_dict['TMAX'] = np.max(temps)
    date_dict['TAVG']=np.mean(temps)


    jsonDict= jsonify(date_dict)
    return (jsonDict)


@app.route("/api/v1.0/<start>/<end>")
def startEnd(start,end):
    
    startStr = start
    endStr = end
    startDate= dt.datetime.strptime(startStr, "%Y-%m-%d").date()
    endDate= dt.datetime.strptime(endStr, "%Y-%m-%d").date()

    session = Session(engine)
    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates from the start date through the end date (inclusive).
    results = session.query(Measurement.date,Measurement.tobs).all()
    session.close

    temps =[]
    date_dict = {}
    for date,tobs in results:

        newDate= dt.datetime.strptime(date, "%Y-%m-%d").date()
                
        if (newDate >= startDate)and(newDate <= endDate):
            temps.append(tobs)

    date_dict['TMIN'] = np.min(temps)
    date_dict['TMAX'] = np.max(temps)
    date_dict['TAVG']=np.mean(temps)


    jsonDict= jsonify(date_dict)
    return (jsonDict)


if __name__ == "__main__":
    app.run(debug=True)
