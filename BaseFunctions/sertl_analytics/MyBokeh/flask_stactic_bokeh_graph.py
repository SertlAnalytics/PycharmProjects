"""
Description: This module contains different functions for Flast with Bokeh server.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""

from flask import Flask, render_template
from datetime import datetime
from BasicLine import div, js, cdn_css, cdn_js


class MyFlask:
    def __init__(self):
        pass

    def start_flask(self):
        app = Flask(__name__)

        @app.route("/")
        def index():
            return render_template('index_static.html',
                                   current_date=datetime.now(), js=js, div=div,
                                   cdn_js=cdn_js, cdn_css=cdn_css)

        app.run(debug=True)


if __name__ == "__main__":
    my_flask = MyFlask()
    my_flask.start_flask()



