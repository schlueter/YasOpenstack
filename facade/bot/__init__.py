import re
from pprint import pformat

from facade import log
from facade.openstack.server import ServerManager, ServersFoundException, NoServersFound


server_manager = ServerManager()

def list_handler(search_opts, result_fields):
    if search_opts:
        search_opts = dict([opt.split('=') for opt in search_opts.split(' ')])
    else:
        search_opts = {}
    if result_fields:
        result_fields.split(',')
    else:
        result_fields = ['name', 'tags', 'description', 'status', 'addresses']
    try:
        servers = server_manager.findall(**search_opts)
    except ServersFoundException as e:
        return str(e)

    log(f'parsing {len(servers)} servers...')
    servers = [server.to_dict() for server in servers]
    server_info = {}
    for server in servers:
        name = server.get('name', 'unknown')
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

def create_handler(name, branch):
    server = server_manager.create(name)
    log(f'Created {server}')
    response = f'Requested creation of {name}'
    if branch:
        response += 'on {branch}'
    return response


def delete_handler(name):
    try:
        result = server_manager.delete(name=f'^{name}$')
    except ServersFoundException as e:
        return str(e)
    log(f'Deleted {name}')
    return f'Successfully deleted {name}.'

handlers = {
    re.compile('(?:list)\ ?([a-z\.=,]+)?(?:\ fields\ )?([\-a-zA-Z0-9\,_]+)?'): list_handler,
    re.compile('(?:launch|start|create)\ ([-\w]+)(?:\ on\ )?([-\w]+:?[-\w]+)?'): create_handler,
    re.compile('(?:delete|drop|terminate|bust a cap in|pop a cap in) ([-\ \w]+)'): delete_handler
}
