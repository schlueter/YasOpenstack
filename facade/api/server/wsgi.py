# Copyright 2017 Brandon Schlueter
# pylint: disable=no-self-use

import os

from flask import Flask
from flask_restful import reqparse, Api, Resource

from novaclient import client


OS_COMPUTE_VERSION = os.environ.get('OS_COMPUTE_VERSION', 2)
OS_USERNAME = os.environ.get('OS_USERNAME')
OS_PASSWORD = os.environ.get('OS_PASSWORD')
OS_PROJECT_NAME = os.environ.get('OS_PROJECT_NAME')
OS_AUTH_URL = os.environ.get('OS_AUTH_URL')
OS_PROJECT_DOMAIN_NAME = os.environ.get('OS_PROJECT_DOMAIN_NAME', 'default')
OS_USER_DOMAIN_NAME = os.environ.get('OS_USER_DOMAIN_NAME', 'default')

NOVA = client.Client(version=OS_COMPUTE_VERSION,
                     username=OS_USERNAME,
                     password=OS_PASSWORD,
                     project_name=OS_PROJECT_NAME,
                     auth_url=OS_AUTH_URL,
                     project_domain_name=OS_PROJECT_DOMAIN_NAME,
                     user_domain_name=OS_USER_DOMAIN_NAME)

class Ping(Resource):
    def get(self):
        return {"response": "pong"}

class ServerList(Resource):

    def get(self):
        return [server.to_dict() for server in NOVA.servers.list()]

def initialize_application():

    app = Flask(__name__)
    api = Api(app)

    parser = reqparse.RequestParser()
    parser.add_argument('task')

    api.add_resource(Ping, '/ping')
    api.add_resource(ServerList, '/server/list')

    app.run(debug=True)
