from flask import Flask, jsonify, render_template

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy as sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

app = Flask(__name__)

engine = create_engine('sqlite:///Resources/hawaii.sqlite', connect_args = {'check_same_thread': False})
session = Session(bind = engine)
conn = engine.connect()
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station

latest_date_str = session.query(Measurement).order_by(Measurement.date.desc()).first().date
latest_date = dt.datetime.strptime(latest_date_str, '%Y-%m-%d')
one_year_ago_date = latest_date - dt.timedelta(days = 365)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/chart_page')
def chart():
    return render_template('chart_page.html')

@app.route('/endpoint')
def endpoint():
    prec = {"test": "Linlin again"}
    return jsonify(prec)

@app.route('/api/v1.0/precipitation')
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago_date).all()
    prec = {result[0]:result[1] for result in results}
    return jsonify(prec)

@app.route('/api/v1.0/stations')
def stations():
    results = session.query(Station.station).all()
    final_result = list(np.ravel(results))
    return jsonify(stations = final_result)

@app.route('/api/v1.0/tobs')
def tobs():
    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date > one_year_ago_date).all()
    final_result = list(np.ravel(results))
    return jsonify(temps = final_result)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def stats(start, end = None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results = session.query(*sel).filter(Measurement.date > start).all()
        final_result = list(np.ravel(results))
        return jsonify(temps = final_result)
    else:
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        final_result = list(np.ravel(results))
        return jsonify(temps = final_result)
if __name__ == '__main__':
    app.run(debug = True)
    import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save reference to the table
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
def Home_page():
    """List all available api routes."""
    return (
        f"Available Routes:<br>"
        f"==================================================<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start><end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(bind = engine)
    # Query all prcp
    dates = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    dates # datetime.date(2016, 8, 23)
    # Perform a query to retrieve the data and precipitation scores
    precipitation_scores = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= "2016-08-23").\
    order_by(Measurement.date).all()
    #precip_df = pd.DataFrame(precipitation_scores, columns=['Date', 'Precipitation'])
    #return jsonify([precip_df['Date'],precip_df['Precipitation']])
    #return jsonify([precip_df['Precipitation'].to_list()])
    return jsonify({date_1:temperature for date_1, temperature in precipitation_scores})
    
@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    session = Session(bind = engine)
    #     """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all stations
    results = session.query(Station.station, Station.name).all()
    session.close()
#     Station_list = list(results) #list(np.ravel(results))
    Station_list = []
    for stat in results:
        d = {
        "Station":stat[0],
        "Station Name":stat[1]
        }
        Station_list.append(d)
    
    return jsonify(Station_list)

@app.route("/api/v1.0/tobs")
# Return a JSON list of temperature observations (TOBS) for the previous year
def tobs():
    session = Session(engine)
    dates = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    dates # datetime.date(2016, 8, 23)
    # Query all stations
    results = session.query(Measurement.date, Measurement.tobs)\
                .filter(Measurement.station == 'USC00519281', Measurement.date.between(dates, dt.date(2017, 8, 23)))\
                .group_by(Measurement.date)\
                .order_by(Measurement.date)
    session.close()
#     temp_obser_12 = list(np.ravel(results))
    tobs_list = []
    for tobs in results:
        d={
        "Date":tobs[0],
        "Temperature":tobs[1]
        }
        tobs_list.append(d)
    return jsonify(tobs_list)

# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
# Start Day Route

if __name__ == '__main__':
    app.run(debug=True)