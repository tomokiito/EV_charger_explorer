from .forms import SearchForm
from .services import get_stations_near
from .services import autocomplete_address

import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify


load_dotenv()  # take environment variables from .env.

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

@app.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        address = form.address.data
        stations = get_stations_near(address)
        return render_template('stations.html', stations=stations)
    return render_template('search.html', form=form)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q', '')
    if len(query) > 2:
        results = autocomplete_address(query)
        return jsonify(results)
    else:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)