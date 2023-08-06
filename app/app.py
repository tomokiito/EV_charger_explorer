from EV_charger_explorer.app.forms import SearchForm
from EV_charger_explorer.app.services import get_stations_near

import os
from dotenv import load_dotenv
from flask import Flask, render_template, request


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

if __name__ == '__main__':
    app.run(debug=True)