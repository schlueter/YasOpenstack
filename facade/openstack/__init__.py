import os
from collections import namedtuple

from novaclient.client import Client as NovaClient

from facade.openstack.yaml_file_config import YamlConfiguration


class Client:
    def __init__(self):
        self.config = YamlConfiguration()
        self._novaclient = novaclient.Client(
            version=self.config.compute_version,
            username=self.config.username,
            password=self.config.password,
            project_name=self.config.project_name,
            auth_url=self.config.auth_url,
            project_domain_name=self.config.project_domain_name,
            user_domain_name=self.config.user_domain_name
        )
        self.servers = self._novaclient.servers

ServerCreationDefaults = namedtuple('ServerCreationDefaults', [
    'image',
    'flavor',
    'security_groups',
    'userdata',
    'key_name',
    'nics'
])
