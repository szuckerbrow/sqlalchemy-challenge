# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
# session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return(
        f"Welcome to the Honolulu weather API!<br/><br/>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation - this will return the precipation data for Honolulu, Hawaii.<br/>"
        f"/api/v1.0/stations - this will provide a list of stations.<br/>"
        f"/api/v1.0/tobs - this will provide a list of temperatures from the last year.<br/>"
        f"/api/v1.0/<start> - replace start with a date of your choosing (date must be in YYYY-MM-DD format, for example: /api/v1.0/2022-01-01). This link will return min, max, and avg temps for that date.<br/>"
        f"/api/v1.0/<start>/<end> - replace start and end with a date (YYYY-MM-DD). This will return min, max, and avg temps for that date range."
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # create session for this thread
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    most_recent_dt = dt.date(2017, 8, 23)
    one_year_ago = most_recent_dt - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precip_data_year = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in precip_data_year}

    #close session for this thread
    session.close()

    # Return the data as JSON
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # create session for this thread
    session = Session(engine)

    # Return list of stations
    stations_list = session.query(Station.station).all()
    print(stations_list)

    station_code = [result[0] for result in stations_list]
    
    #close session for this thread
    session.close()
    
    # Return the data as JSON
    return jsonify(station_code)
   

@app.route("/api/v1.0/tobs")
def tobs():
    # create session for this thread
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    most_recent_dt = dt.date(2017, 8, 23)
    one_year_ago = most_recent_dt - dt.timedelta(days=365)

    # Perform a query to retrieve the data and temperatures
    most_active_station_temps_year = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= one_year_ago).\
    filter(Measurement.station == 'USC00519281').all()

    temps = [result[1] for result in most_active_station_temps_year]

    #close session for this thread
    session.close()
    
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def temp_stats(start):
    # create session for this thread
    session = Session(engine)

    most_recent_dt = dt.date(2017, 8, 23)
     
    # get min, max, and avg temp for most active station and specified date in the url
    most_active_station_stats = session.query(
        func.min(Measurement.tobs).label("min_temp"), 
        func.max(Measurement.tobs).label("max_temp"), 
        func.avg(Measurement.tobs).label("avg_temp")
            ).filter(Measurement.date >= start).\
            filter(Measurement.date <= most_recent_dt).\
            filter(Measurement.station == 'USC00519281').first()

    #close session for this thread
    session.close()
    
    # Return the data as Json
    return jsonify({
        "start_date":start,
        "min_temperature": most_active_station_stats.min_temp,
        "max_temperature": most_active_station_stats.max_temp,
        "avg_temperature": most_active_station_stats.avg_temp
    })

@app.route("/api/v1.0/<start>/<end>")
def temp_date_range(start=None, end=None):
    # create session for this thread
    session = Session(engine)

    sel=[func.min(Measurement.tobs).label("min_temp"), func.max(Measurement.tobs).label("max_temp"), func.avg(Measurement.tobs).label("avg_temp")]

    date_range_temps = session.query(*sel).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).first()
    
    #close session for this thread
    session.close()

    return(jsonify)({
        "start_date":start,
        "end_date":end,
        "min_temp":date_range_temps.min_temp,
        "max_temp":date_range_temps.max_temp,
        "avg_temp":date_range_temps.avg_temp
    })

if __name__ == "__main__":
    app.run(debug=True)

