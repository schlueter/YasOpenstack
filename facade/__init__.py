import os
import re
from pprint import pformat

from jinja2 import Template
from novaclient.exceptions import BadRequest
from yas import YasHandler

from facade.openstack.server import ServerManager, ServersFoundException
from facade.openstack.yaml_file_config import YamlConfiguration


config = YamlConfiguration()

class OpenstackHandlerError(Exception):
    pass

class OpenstackHandler(YasHandler):

    def __init__(self, bot_name, api_call, *args, log=None, **kwargs):
        super().__init__(bot_name, api_call, *args, **kwargs)
        self.log('DEBUG', f'Initializing Openstack handler with config:\n{config.__dict__}')
        self.handlers = {
            re.compile('(?:list)\ ?([a-z\.=,]+)?(?:\ fields\ )?([\-a-zA-Z0-9\,_]+)?'): self.list_handler,
            re.compile('(?:launch|start|create)\ ([-\w]+)(?:\ on\ )?([-\w]+:?[-\w]+)?'): self.create_handler,
            re.compile('(?:delete|drop|terminate|bust a cap in|pop a cap in) ([-\ \w]+)'): self.delete_handler
        }
        self.server_manager = ServerManager()
        self.matches = {}
        self.template = self.get_userdata_template()

    def get_userdata_template(self):
        config_userdata = config.create_server_defaults.get('userdata', '')
        potential_userdata_file = os.path.join(sys.prefix, config_userdata)
        if os.path.isfile(potential_userdata_file):
            template_file = open(potential_userdata_file, 'r')
            template = template_file.read()
            template_file.close()
        else:
            template = config_userdata

        return Template(self.userdata_template)

    def test(self, data):
        for regexp in self.handlers:
            match = regexp.search(data.get('text', ''))
            if match:
                self.matches[data['yas_hash']] = (self.handlers[regexp], match)
                return True

    def handle(self, data, reply):
        handler, match = self.matches.pop(data['yas_hash'])
        groups = match.groups()
        try:
            response = handler(data, *groups)
        except BadRequest as e:
            raise OpenstackHandlerError(e)
        return reply(response)

    def create_handler(self, data, name, branch):
        response = f'Requesting creation of {name}'

        userdata = self.template.render(name=name, branch=branch, **data)

        server = self.server_manager.create(name, userdata=userdata)
        self.log('INFO', f'Created {server}')
        self.log('DEBUG', f'Used userdata:\n{userdata}')
        if branch:
            response += 'on {branch}'
        return response


    def delete_handler(self, name):
        try:
            result = self.server_manager.delete(name=f'^{name}$')
        except ServersFoundException as e:
            return str(e)
        self.log('INFO', f'Deleted {name}')
        return f'Successfully deleted {name}.'

    def list_handler(self, search_opts, result_fields):
        if search_opts == 'all':
            if not result_fields:
                result_fields = 'all'
            search_opts = None

        if search_opts:
            search_opts = dict([opt.split('=') for opt in search_opts.split(' ')])
        else:
            search_opts = {}
        if result_fields:
            result_fields.split(',')
        else:
            result_fields = ['name', 'tags', 'description', 'status', 'addresses']
        try:
            servers = self.server_manager.findall(**search_opts)
        except ServersFoundException as e:
            return str(e)

        self.log('INFO', f'parsing {len(servers)} servers...')
        servers = [server.to_dict() for server in servers]
        server_info = {}
        for server in servers:
            name = server.get('name', 'unknown')
            if 'all' in result_fields:
                server_info[name] = server
                continue
            server_info[name] = {}
            if 'addresses' in result_fields:
                server_info[name]['addresses'] = [interface['addr']
                                                  for provider in server['addresses']
                                                  for interface in server['addresses'][provider]]
                result_fields.remove('addresses')
            if '_addresses' in result_fields:
                result_fields.remove('_addresses')
                result_fields.append('addresses')
            for field in result_fields:
                server_info[name][field] = server[field]
        return pformat(server_info)
