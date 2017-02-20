# Copyright 2017 Brandon Schlueter
# pylint: disable=no-self-use

from flask import Flask
from flask_restful import reqparse, Api, Resource

class Ping(Resource):
    def get(self):
        return "pong"


def initialize_application():

    app = Flask(__name__)
    api = Api(app)

    parser = reqparse.RequestParser()
    parser.add_argument('task')

    api.add_resource(Ping, '/ping')

    app.run(debug=True)
