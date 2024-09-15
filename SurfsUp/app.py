# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
SessionFactory = sessionmaker(bind=engine)
session = scoped_session(SessionFactory)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Route for the home page
@app.route("/")
def home():
    return """
    Available Routes:<br>
    /api/v1.0/precipitation<br>
    /api/v1.0/stations<br>
    /api/v1.0/tobs<br>
    /api/v1.0/&lt;start_date&gt;<br>
    /api/v1.0/&lt;start_date&gt;/&lt;end_date&gt;
    """

# Route for precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    precip_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    precip_dict = {date: prcp for date, prcp in precip_data}
    return jsonify(precip_dict)

# Route for stations data
@app.route("/api/v1.0/stations")
def stations():
    stations_data = session.query(Station.station).all()
    stations_list = list(np.ravel(stations_data))
    return jsonify(stations_list)

# Route for temperature observations for the most active station
@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station_id = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    tobs_data = session.query(Measurement.tobs).filter(Measurement.station == most_active_station_id, Measurement.date >= one_year_ago).all()
    tobs_list = list(np.ravel(tobs_data))
    return jsonify(tobs_list)

# Route for temperature statistics for a single start date
@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    """Return a list of min, avg, and max tobs for a start date"""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).all()

    # Create a dictionary from the row data and return it
    start_date_tobs = []
    for min_temp, avg_temp, max_temp in results:
        start_date_tobs_dict = {
            "min_temp": min_temp,
            "avg_temp": avg_temp,
            "max_temp": max_temp
        }
        start_date_tobs.append(start_date_tobs_dict) 

    return jsonify(start_date_tobs)

# Route for temperature statistics between start and end dates
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_date(start_date, end_date):
    """Return a list of min, avg and max tobs for start and end dates"""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Create a dictionary from the row data and return it
    start_end_tobs = []
    for min_temp, avg_temp, max_temp in results:
        start_end_tobs_dict = {
            "min_temp": min_temp,
            "avg_temp": avg_temp,
            "max_temp": max_temp
        }
        start_end_tobs.append(start_end_tobs_dict)

    return jsonify(start_end_tobs)

@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

if __name__ == "__main__":
    app.run(debug=True)