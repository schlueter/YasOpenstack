# Copyright 2017 Brandon Schlueter
# pylint: disable=no-self-use

import os

from flask import Flask
from flask_restful import reqparse, Api, Resource

from facade.openstack.server import ServerManager

# 2.38 is the highest valid version as of date of commit
PORT = os.environ.get('FACADE_PORT', 5001)

servers = ServerManager()

class Ping(Resource):
    def get(self):
        return {"response": "pong"}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("message")
        args = parser.parse_args()
        return {"response": args["message"]}


class Server(Resource):
    def post(self, name, creator):
        server = servers.create(
            name=name,
            image=serv.glance.find_image('ubuntu/trusty64'),
            flavor=[flavor for flavor in NOVA.flavors.list() if flavor.name == 'm1.big'],
            # TODO requires neutron client
            security_groups=['344188ea-7747-4a67-8517-743e99799fda'],
            userdata='',
            key_name='bs',
            # TODO requires neutron client
            nics=[{
                "net-id": '832bbfef-7ebd-4da5-8029-f7cf89e4ee5e',
                "v4-fixed-ip": ''
            }]
        )
        server.tag('creator={}'.format(creator))

        return '', 202

    def delete(self, name):
        server = [server for server in NOVA.servers.list() if server.name == name][0]
        server.delete()
        return '', 204

class ServerList(Resource):
    def get(self):
        return [server.to_dict() for server in NOVA.servers.list()], 200

def wsgi_app():
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Ping, '/ping')
    api.add_resource(ServerList, '/server/list')

    app.run(port=PORT, debug=True)
