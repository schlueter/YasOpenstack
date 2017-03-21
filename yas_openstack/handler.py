import re
import sys
from pprint import pformat

from novaclient.exceptions import BadRequest
from yas import YasHandler

from yas_openstack.server import ServerManager, ServersFoundException, NoServersFound

class OpenstackHandlerError(Exception):
    pass

class OpenstackHandler(YasHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handlers = {
            re.compile('(?:list)\ ?([a-z\.=,]+)?(?:\ fields\ )?([\-a-zA-Z0-9\,_]+)?'): self.list_handler,
            re.compile('(?:launch|start|create)\ ([-\w]+)(?:\ on\ )?([-\w]+:?[-\w]+)?'): self.create_handler,
            re.compile('(?:delete|drop|terminate|bust a cap in|pop a cap in) ([-\ \w]+)'): self.delete_handler
        }
        self.server_manager = ServerManager()
        self.matches = {}

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
            response = handler(*groups)
        except BadRequest as e:
            raise OpenstackHandlerError(e)
        return reply(response)

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

    def create_handler(self, name, branch):
        server = self.server_manager.create(name)
        self.log('INFO', f'Created {server}')
        response = f'Requested creation of {name}'
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


