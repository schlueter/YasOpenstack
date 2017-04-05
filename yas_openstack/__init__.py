import os
from collections import namedtuple

import novaclient.client
import openstack.connection

from yas_openstack.yaml_file_config import YamlConfiguration

config = YamlConfiguration()

class Client:
    def __init__(self):
        self._os_connection = openstack.connection.Connection(
            auth_url=config.auth_url,
            username=config.username,
            password=config.password,
            project_name=config.project_name,
            project_domain_name=config.project_domain_name,
            user_domain_name=config.user_domain_name
        )
        self._novaclient = novaclient.client.Client(
            version=config.compute_version,
            username=config.username,
            password=config.password,
            project_name=config.project_name,
            auth_url=config.auth_url,
            project_domain_name=config.project_domain_name,
            user_domain_name=config.user_domain_name
        )
        self.image = self._os_connection.image
        self.compute = self._os_connection.compute
        self.servers = self._novaclient.servers
        self.create_server_defaults = config.create_server_defaults
