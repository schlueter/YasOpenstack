import os
from collections import namedtuple

import novaclient.client
import openstack.connection

from yas_openstack.yaml_file_config import YamlConfiguration

CONFIG = YamlConfiguration()

class Client:
    def __init__(self):
        self._os_connection = openstack.connection.Connection(
            auth_url=CONFIG.auth_url,
            username=CONFIG.username,
            password=CONFIG.password,
            project_name=CONFIG.project_name,
            project_domain_name=CONFIG.project_domain_name,
            user_domain_name=CONFIG.user_domain_name
        )
        self._novaclient = novaclient.client.Client(
            version=CONFIG.compute_version,
            username=CONFIG.username,
            password=CONFIG.password,
            project_name=CONFIG.project_name,
            auth_url=CONFIG.auth_url,
            project_domain_name=CONFIG.project_domain_name,
            user_domain_name=CONFIG.user_domain_name
        )
        self.image = self._os_connection.image
        self.compute = self._os_connection.compute
        self.servers = self._novaclient.servers
        self.create_server_defaults = CONFIG.create_server_defaults
