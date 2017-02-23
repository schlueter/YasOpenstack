import os
from collections import namedtuple


from novaclient import client as novaclient


OS_COMPUTE_VERSION = os.environ.get('OS_COMPUTE_VERSION', '2.38')
OS_USERNAME = os.environ.get('OS_USERNAME')
OS_PASSWORD = os.environ.get('OS_PASSWORD')
OS_PROJECT_NAME = os.environ.get('OS_PROJECT_NAME')
OS_AUTH_URL = os.environ.get('OS_AUTH_URL')
OS_PROJECT_DOMAIN_NAME = os.environ.get('OS_PROJECT_DOMAIN_NAME', 'default')
OS_USER_DOMAIN_NAME = os.environ.get('OS_USER_DOMAIN_NAME', 'default')

class Client(object):
    def __init__(self):
        self._novaclient = novaclient.Client(
            version=OS_COMPUTE_VERSION,
            username=OS_USERNAME,
            password=OS_PASSWORD,
            project_name=OS_PROJECT_NAME,
            auth_url=OS_AUTH_URL,
            project_domain_name=OS_PROJECT_DOMAIN_NAME,
            user_domain_name=OS_USER_DOMAIN_NAME
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
