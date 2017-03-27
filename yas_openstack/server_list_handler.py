from pprint import pformat

from yas_openstack.openstack_handler import OpenStackHandler
from yas_openstack.server import ServersFoundException


class OpenStackServerListHandler(OpenStackHandler):

    def __init__(self, regex, bot_name, api_call, *args, log=None, **kwargs):
        super().__init__('(?:list)\ ?([a-z\.=,]+)?(?:\ fields\ )?([\-a-zA-Z0-9\,_]+)?',
                         bot_name, api_call, *args, log=log, **kwargs)

    def handle(self, data, reply):
        search_opts, result_fields = self.current_match.groups()
        if search_opts == 'all':
            if not result_fields:
                result_fields = 'all'
            search_opts = None

        if search_opts:
            search_opts = dict(opt.split('=') for opt in search_opts.split(' '))
        else:
            search_opts = {}
        if result_fields:
            result_fields.split(',')
        else:
            result_fields = ['name', 'metadata', 'status', 'addresses']

        reply(f"Preparing listing of {search_opts or 'all'} with {result_fields}", thread=data['ts'])

        try:
            servers = self.server_manager.findall(**search_opts)
        except ServersFoundException as e:
            reply(f'There was an issue finding {name}: {e}', thread=data['ts'])

        self.log('INFO', f'parsing {len(servers)} servers...')
        servers = [server.to_dict() for server in servers]
        server_info = {}
        for server in servers:
            id = server.get('id')
            name = server.get('name')
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
        reply(pformat(server_info), thread=data['ts'])

