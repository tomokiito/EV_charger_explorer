from .forms import SearchForm
from .services import get_stations_near
from .services import autocomplete_address
from .services import register_to_database
from .services import get_stations_from_database
from .services import delete_station_from_database
from .services import analyze_stations



import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from datetime import datetime


load_dotenv()  # take environment variables from .env.

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY')
app.config['MONGODB_URI'] = os.getenv('MONGODB_URI')


# To store the number of requests and the last request time
request_data = {
    "total_requests": 0,
    "last_request_time": None
}

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200


@app.route('/metrics', methods=['GET'])
def metrics():
    current_time = datetime.now()
    time_difference = (current_time - request_data["last_request_time"]).total_seconds() if request_data["last_request_time"] else 0
    requests_per_second = request_data["total_requests"] / time_difference if time_difference != 0 else 0

    return jsonify({
        "requests_per_second": requests_per_second
    }), 200


@app.before_request
def before_request():
    request_data["total_requests"] += 1
    request_data["last_request_time"] = datetime.now()



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
    success, station_object_id = register_to_database(app.config['MONGODB_URI'], station_data)

    if success:
        response = {"message": "Data registered successfully!", "station_object_id": str(station_object_id)}
    else:
        response = {"error": "Failed to register data"}

    return jsonify(response)


@app.route('/get_stations', methods=['GET'])
def get_stations():
    stations = get_stations_from_database(app.config['MONGODB_URI'])
    return jsonify(stations)


@app.route('/delete_station', methods=['POST'])
def delete_station():
    station_data = request.json
    station_id = station_data["_id"]
    success = delete_station_from_database(app.config['MONGODB_URI'], station_id)

    if success:
        response = {"message": "Data deleted successfully!"}
    else:
        response = {"error": "Failed to delete data"}

    return jsonify(response)


@app.route('/analyze', methods=['GET'])
def analyze():
    # Get charging stations from the database
    db_stations = get_stations_from_database(app.config['MONGODB_URI'])

    # Analyze the stations
    analysis_result = analyze_stations(db_stations)

    # Log the analysis result
    print("Analysis Result:", analysis_result)

    # Return the analysis result as JSON
    return jsonify(analysis_result)


if __name__ == '__main__':
    app.run(debug=True)
