from .forms import SearchForm
from .services import get_stations_near
from .services import autocomplete_address
from .services import register_to_database
from .services import get_stations_from_database

import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient


load_dotenv()  # take environment variables from .env.

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY')
app.config['MONGODB_URI'] = os.getenv('MONGODB_URI')


@app.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    db_stations = get_stations_from_database(app.config['MONGODB_URI']) 
    if form.validate_on_submit():
        address = form.address.data
        stations = get_stations_near(address)
        return render_template('stations.html', stations=stations, google_maps_api_key=app.config['GOOGLE_MAPS_API_KEY'])
    return render_template('search.html', form=form, db_stations=db_stations) 


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q', '')
    if len(query) > 2:
        results = autocomplete_address(query)
        return jsonify(results)
    else:
        return jsonify([])


@app.route('/register', methods=['POST'])
def register_station():
    # Get the posted data
    station_data = request.json

    # Validate data
    required_keys = ['Title', 'ID', 'ConnectionTypeID', 'StatusTypeID', 'LevelID']
    if not all(key in station_data for key in required_keys):
        response = {"error": "Failed to register data - missing required fields"}
        return jsonify(response), 400

    # Register data to the database
    success = register_to_database(app.config['MONGODB_URI'], station_data)

    if success:
        response = {"message": "Data registered successfully!"}
    else:
        response = {"error": "Failed to register data"}

    return jsonify(response)


@app.route('/get_stations', methods=['GET'])
def get_stations():
    stations = get_stations_from_database(app.config['MONGODB_URI'])
    return jsonify(stations)


if __name__ == '__main__':
    app.run(debug=True)
