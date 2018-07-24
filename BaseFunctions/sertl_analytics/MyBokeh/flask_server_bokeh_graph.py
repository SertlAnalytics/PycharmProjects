"""
Description: This module contains different functions for Flask with Bokeh server.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""

from flask import Flask, render_template
from bokeh.embed import server_document


class MyFlask:
    def __init__(self):
        pass

    def start_flask(self):
        app = Flask(__name__)

        @app.route("/")
        def index():
            bokeh_script = server_document(url='http://localhost:5006/random_generator')
            return render_template('index_server.html', bokeh_script=bokeh_script)

        app.run(debug=True)


if __name__ == "__main__":
    my_flask = MyFlask()
    my_flask.start_flask()



