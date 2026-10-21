from pyowm import OWM
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect
from pyzipcode import ZipCodeDatabase
from pyowm.commons.exceptions import (
    NotFoundError,
    UnauthorizedError,
    APIRequestError,
    APIResponseError
)
import os


"""
    This program retrives the weather based on a Zipcode, City and Country or City, State and Country.

    This program is broken into 3 functions
                                                                                                        !
    internal_server_error: Renders 500 error page if program recieves a 500 error handler
    index: Renders the weather.html
    search: Retrieves POST data from weather.html form. Gets Location from Zip code and weather from
             the location.
"""

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or os.urandom(32)
csrf = CSRFProtect(app)
owm = OWM(os.environ['API'])

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

@app.route('/')
def index():
    return render_template('weather.html')


@app.route('/search', methods=['POST'])
def search():

    """
        Function recieves the location from form.
        Runs through basic IF to verify variable has data
        Second IF verifies if it is a Zipcode. If it is, uses pyzipcode to retrieve City, State.
        Lastly, gathers weather information from location using pyowm.
        Renders data to city.html
    """

    search = request.form.get('response', '').strip()
    if not search:
        return render_template('invalid.html', error='No location provided'), 400
    
    if search.isascii() and search.isdigit() and len(search) == 5:
        zcdb = ZipCodeDatabase()
        try:
            zipcode = zcdb[search]
            location = f"{zipcode.city}, {zipcode.state}, US"
        except (KeyError, IndexError):
            return render_template('invalid.html', error='Invalid Zipcode'), 400
    else:
        location = search
    try:
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(location)
        w = observation.weather
        ftemp = w.temperature(unit='fahrenheit')['temp']
        ctemp = w.temperature(unit='celsius')['temp']
        descript = w.detailed_status

    except NotFoundError:
        app.logger.warning("Weather location not found: %s", location)
        return render_template('invalid.html', error='Weather location not found'), 404
    except UnauthorizedError:
        app.logger.error("OpenWeatherMap API authorization failed")
        return render_template('500.html'), 502

    except APIRequestError:
        app.logger.exception("OpenWeatherMap connection failed")
        return render_template('500.html'), 503

    except APIResponseError:
        app.logger.exception("OpenWeatherMap returned an API error")
        return render_template('500.html'), 502

    weather = {
        'location': location,
        'current': descript,
        'ftemp': ftemp,
        'ctemp': ctemp,
    }
    return render_template("city.html", weather=weather)