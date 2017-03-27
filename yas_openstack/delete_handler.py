from yas_openstack import OpenstackHandler
from yas_openstack.server import ServersFoundException


class OpenStackServerDeleteHandler(OpenStackHandler):

    def __init__(self, regex, bot_name, api_call, *args, log=None, **kwargs):
        super().__init__('(?:delete|drop|terminate|bust a cap in|pop a cap in) ([-\ \w]+)',
                         bot_name, api_call, *args, log=log, **kwargs)

    def handler(self, data, reply):
        name = self.current_match.groups()[0]
        reply(f"Requesting deletion of {name}", thread=data['ts'])

        try:
            result = self.server_manager.delete(name=f'^{name}$')
        except ServersFoundException as e:
            return reply(f'There was an issue finding {name}: {e}', thread=data['ts'])

        self.log('INFO', f'Deleted {name}')
        reply(f'Successfully deleted {name}.', thread=data['ts'])

