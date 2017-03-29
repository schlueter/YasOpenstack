from novaclient.exceptions import Forbidden

from yas_openstack.openstack_handler import OpenStackHandler
from yas_openstack.server import NoServersFound, MultipleServersFound


class OpenStackServerCreateHandler(OpenStackHandler):

    def __init__(self, *args, **kwargs):
        super().__init__('(?:launch|start|create)\ ([-\w]+)'
                         '(?:\ on\ )?([-\w]+:?[-\w]+)?'
                         '(?:\ meta\ )?([\w=,]+)?'
                         '(?:\ from\ )?([-:/\w]+)?',
                         *args, **kwargs)
        self.log('DEBUG', f'Initializing OpenStack server create handler with defaults:\n{self.config.__dict__}')

    def __name_already_used(self, name):
        try:
            existing_server = self.server_manager.find(name=name)
        except NoServersFound:
            existing_server = None
        except MultipleServersFound:
            existing_server = True

        return existing_server

    def handle(self, data, reply):
        name, branch, meta, image = self.current_match.groups()
        self.log('INFO', f"Received request for {name} on {branch} from {image}")
        reply(f"Received request for creation of {name}", thread=data['ts'])

        if self.__name_already_used(name):
            return reply(f"{name} already exists.", thread=data['ts'])

        userdata = self.template.render(meta=meta, name=name, branch=branch or '', data=data)

        try:
            creator_info = self.api_call('users.info', user=data['user'])
        except Exception as e:
            reply(f"Caught {e} while retrieving creator_info.")
            creator_info = None

        if creator_info:
            meta['owner'] = creator_info['user']['profile']['real_name']

        meta['init'] = 'pending'

        meta['branch'] = branch

        try:
            server = self.server_manager.create(name, userdata=userdata, image=image, meta=meta)
        except Forbidden as forbidden:
            if "Quota exceeded" in forbidden.message:
                return reply(forbidden.message)
            raise forbidden

        reply(f'Requested creation of {name} with id {server.id}', thread=data['ts'])
        self.log('DEBUG', f'Created used userdata:\n{userdata}')
