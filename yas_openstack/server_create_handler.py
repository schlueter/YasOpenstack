import json
import os
import sys

from jinja2 import Template
from novaclient.exceptions import Forbidden

from yas_openstack.openstack_handler import OpenStackHandler


def _parse_meta(meta_string):
    if meta_string:
        try:
            meta_dict = dict(pair.split('=') for pair in meta_string.split(','))
        except ValueError:
            raise ValueError('Invalid meta, format must be "key=value,key=value..."')
        for key in meta_dict:
            meta_dict[key] = meta_dict[key] or ''
    else:
        meta_dict = {}
    return meta_dict

class OpenStackServerCreateHandler(OpenStackHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(r'(?:launch|start|create)\ ([-\w]+)'
                         r'(?:\ on\ )?([-\w]+:?[-\w/]+)?'
                         r'(?:\ meta\ )?([\w=,:]+)?'
                         r'(?:\ from\ )?([-:/\w]+)?',
                         *args, **kwargs)
        self.log('DEBUG', f'Initializing OpenStack server create handler with defaults:\n{self.config.__dict__}')
        self.template = self.get_userdata_template()

    def get_userdata_template(self):
        config_userdata = self.config.create_server_defaults.get('userdata', '')
        potential_userdata_file = os.path.join(sys.prefix, config_userdata)

        if os.path.isfile(potential_userdata_file):
            with open(potential_userdata_file, 'r') as template_file:
                template = template_file.read()
        else:
            template = config_userdata

        return Template(template)

    def handle(self, data, reply):
        name, branch, meta_string, image = self.current_match.groups()
        self.log('INFO', f"Received request for {name} on {branch} from {image}")

        creator_info = self._retrieve_user_info(data.get('user', ''))
        if self.server_manager.findall(name=f"^{name}$"):
            return reply(f"{name} already exists.")

        meta = _parse_meta(meta_string)

        if creator_info and 'user' in creator_info:
            meta['owner'] = creator_info['user']['name']
        else:
            meta['owner'] = 'unknown'
        meta['owner_id'] = data.get('user', None) or data.get('bot_id', 'unknown')

        meta['init'] = 'pending'
        meta['branch'] = branch or ''

        userdata = self.template.render(meta=json.dumps(meta), name=name, branch=branch or '', data=data)
        try:
            server = self.server_manager.create(name, userdata=userdata, image=image, meta=meta)
        except Forbidden as forbidden:
            if "Quota exceeded" in forbidden.message:
                return reply(forbidden.message)
            # TODO I dont' know why this is necessary
            # pylint: disable=raising-bad-type
            raise forbidden

        reply(f'Requested creation of {name} with id {server.id}')
        self.log('DEBUG', f'Created used userdata:\n{userdata}')
