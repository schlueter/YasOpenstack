from yas import RegexHandler

from yas_openstack.server import ServerManager
from yas_openstack.yaml_file_config import YamlConfiguration


CONFIG = YamlConfiguration()

class OpenStackHandler(RegexHandler):

    SEARCH_OPTS_REGEX=r'[\w,_=:\.-]+'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server_manager = ServerManager()
        self.matches = {}
        self.config = CONFIG
