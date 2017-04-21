from yas_openstack.openstack_handler import OpenStackHandler
from yas_openstack.server import ServersFoundException


class OpenStackServerDeleteHandler(OpenStackHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(r'(?:delete|drop|terminate|bust a cap in|pop a cap in) ([-\ \w]+)', *args, **kwargs)

    def handle(self, data, reply):
        name = self.current_match.groups()[0]
        try:
            self.server_manager.delete(name=f'^{name}$')
        except ServersFoundException as err:
            self.log('INFO', f'There was an issue finding {name}: {err}')
            return reply(f'There was an issue finding {name}: {err}')

        self.log('INFO', f'Deleted {name}')
        reply(f'Successfully deleted {name}.')
