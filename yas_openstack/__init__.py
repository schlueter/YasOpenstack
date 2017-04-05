import os
from collections import namedtuple

from openstack.connection import Connection

from yas_openstack.yaml_file_config import YamlConfiguration

config = YamlConfiguration()

class OpenStackConnection(Connection):
    def __init__(self):
        super().__init__( auth_url=config.auth_url,
                          username=config.username,
                          password=config.password,
                          project_name=config.project_name,
                          project_domain_name=config.project_domain_name,
                          user_domain_name=config.user_domain_name )
                        # version=config.compute_version,
        self.create_server_defaults = config.create_server_defaults
