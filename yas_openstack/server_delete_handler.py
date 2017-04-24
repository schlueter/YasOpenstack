from yas_openstack.openstack_handler import OpenStackHandler
from yas_openstack.server import ServersFoundException


class OpenStackServerDeleteHandler(OpenStackHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(r'(?:delete|drop|terminate|bust a cap in|pop a cap in) ([-\ \w]+)', *args, **kwargs)

    def handle(self, data, reply):
        names = self.current_match.groups()[0].split()
        for name in names:
            reply(f"Requesting deletion of {name}", thread=data['ts'])

            try:
                self.server_manager.delete(name=f'^{name}$')
            except ServersFoundException as err:
                return reply(f'There was an issue finding {name}: {err}', thread=data['ts'])

            self.log('INFO', f'Deleted {name}')
            reply(f'Successfully deleted {name}.', thread=data['ts'])
