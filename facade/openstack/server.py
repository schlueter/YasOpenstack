# Copyright 2017 Refinery29

from facade.openstack import Client
from facade.openstack.config import server_creation_defaults as defaults

class ServersFoundException(Exception):
    pass

class NoServersFound(ServersFoundException):
    def __init__(self):
        super().__init__('No servers found matching the specified search options. Refer to <https://developer.openstack.org/api-ref/compute/?expanded=list-servers-detail#id4|the docs> for available search parameters.')

class MultipleServersFound(ServersFoundException):
    def __init__(self, servers):
        super().__init__(f'Found multiple servers: {[dict(name=server.name, id=server.id) for server in servers].join(", ")}\n\nRefer to <https://developer.openstack.org/api-ref/compute/?expanded=list-servers-detail#id4|the docs> for available search parameters to make your query more specific.')


class ServerManager(Client):

    def create(self,
               name,
               image=defaults.image,
               flavor=defaults.flavor,
               security_groups=defaults.security_groups,
               userdata=defaults.userdata,
               key_name=defaults.key_name,
               nics=defaults.nics):
        return self.servers.create(name,
                                   image=image,
                                   flavor=flavor,
                                   security_groups=security_groups,
                                   userdata=userdata,
                                   key_name=key_name,
                                   nics=nics)

    def delete(self, **kwargs):
        server = self.find(**kwargs)
        return server.delete()

    def find(self, detailed=True, **kwargs):
        search_results = self.servers.list(detailed=detailed, search_opts=kwargs)

        if len(search_results) == 0:
            raise NoServersFound

        if len(search_results) > 1:
            raise MultipleServersFound(search_results)

        return search_results[0]

    def findall(self, detailed=True, **kwargs):
        return self.servers.list(detailed=detailed, search_opts=kwargs)
