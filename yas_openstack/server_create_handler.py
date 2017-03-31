import json

from novaclient.exceptions import Forbidden

from yas_openstack.openstack_handler import OpenStackHandler
from yas_openstack.server import NoServersFound, MultipleServersFound


def _parse_meta(meta_string):
    if meta_string:
        try:
            meta_dict = dict(pair.split('=') for pair in meta_string.split(','))
        except ValueError as e:
            raise ValueError('Invalid meta, format must be "key=value,key=value..."')
        for key in meta_dict:
            meta_dict[key] = meta_dict[key] or ''
    else:
        meta_dict = {}
    return meta_dict

class OpenStackServerCreateHandler(OpenStackHandler):

    def __init__(self, *args, **kwargs):
        super().__init__('(?:launch|start|create)\ ([-\w]+)'
                         '(?:\ on\ )?([-\w]+:?[-\w]+)?'
                         '(?:\ meta\ )?([\w=,]+)?'
                         '(?:\ from\ )?([-:/\w]+)?',
                         *args, **kwargs)
        self.log('DEBUG', f'Initializing OpenStack server create handler with defaults:\n{self.config.__dict__}')
        self.creators = [self._retrieve_user_id(username) for username in self.config.creator_list]
        self.creators.append('')

    def handle(self, data, reply):
        name, branch, meta_string, image = self.current_match.groups()
        self.log('INFO', f"Received request for {name} on {branch} from {image}")

        creator_info = self._retrieve_user_info(data.get('user', ''))
        if not data.get('user', '') in self.creators:
            self.log('INFO', f"Reject creation request from individual not on the list ({data.get('user', 'unknown')}.")
            return reply(f"Sorry, this action is restricted to certain users. Please request access from devops.")

        if self.server_manager.findall(name=name):
            return reply(f"{name} already exists.")

        reply(f"Received request for creation of {name}", thread=data['ts'])

        meta = _parse_meta(meta_string)

        if creator_info:
            meta['owner'] = creator_info['user']['profile']['real_name']
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
            raise forbidden

        reply(f'Requested creation of {name} with id {server.id}', thread=data['ts'])
        self.log('DEBUG', f'Created used userdata:\n{userdata}')
