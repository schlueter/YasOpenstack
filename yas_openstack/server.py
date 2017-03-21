from yas_openstack import Client


class ServerManager(Client):

    def __init__(self):
        super().__init__()
        default_image_name = self.create_server_defaults.get('image_name')
        self.default_image = self.find_image_by_name(default_image_name)

        default_flavor_name = self.create_server_defaults.get('flavor_name')
        self.default_flavor = self.find_flavor_by_name(default_flavor_name)

        self.default_nics=self.create_server_defaults.get('nics')

        self.default_security_groups=self.create_server_defaults.get('security_groups')
        self.default_userdata=self.create_server_defaults.get('userdata')
        self.default_key_name=self.create_server_defaults.get('key_name')

    def find_image_by_name(self, image_name):
        return self._novaclient.glance.find_image(image_name)

    def find_flavor_by_name(self, flavor_name):
        return self._novaclient.flavors.find(name=flavor_name).id

    def create(self, name, **kwargs):
        image = kwargs.get('image') or self.default_image
        flavor = kwargs.get('flavor') or self.default_flavor
        security_groups = kwargs.get('security_groups') or self.default_security_groups
        userdata = kwargs.get('userdata') or self.default_userdata
        key_name = kwargs.get('key_name') or self.default_key_name
        nics = kwargs.get('nics') or self.default_nics

        created_server =  self.servers.create(
            name,
            image=image,
            flavor=flavor,
            userdata=userdata,
            key_name=key_name,
            nics=nics
        )
        return created_server

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


class ServersFoundException(Exception):
    pass


class NoServersFound(ServersFoundException):
    def __init__(self):
        super().__init__('No servers found matching the specified search options. Refer to <https://developer.openstack.org/api-ref/compute/?expanded=list-servers-detail#id4|the docs> for available search parameters.')


class MultipleServersFound(ServersFoundException):
    def __init__(self, servers):
        super().__init__(f'Found multiple servers: {[dict(name=server.name, id=server.id) for server in servers].join(", ")}\n\nRefer to <https://developer.openstack.org/api-ref/compute/?expanded=list-servers-detail#id4|the docs> for available search parameters to make your query more specific.')

