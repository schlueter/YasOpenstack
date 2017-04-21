from pprint import pformat

from yas_openstack.openstack_handler import OpenStackHandler
from yas_openstack.server import ServersFoundException


class OpenStackServerListHandler(OpenStackHandler):

    search_error_message = (
        'Invalid search opts, list query must look like: '
        '```list[ search_opts <sort query>=<argument>[,<query>=<argument>[,...]][ metadata <key>=<value>[,<key>=<value>]]```\n'
        'For example:\n&gt; list search_opts state=Running metadata owner=tswift\n'
        'Available sort queries and fields may be found in the '
        # pylint: disable=line-too-long
        '<https://developer.openstack.org/api-ref/compute/?expanded=list-servers-detailed-detail#list-servers-detailed|docs>.')

    def __init__(self, *args, **kwargs):
        super().__init__(r'(?:list)'
                         r'(?:(?:\ search_opts )([a-z\.=,:\ ]+))?'
                         r'(?:(?:\ metadata\ )([\-a-zA-Z0-9\,_=]+))?',
                         *args, **kwargs)

    def handle(self, data, reply):
        raw_search_opts, raw_metadata = self.current_match.groups()
        self.log('DEBUG', f"Parsed from {data['yas_hash']} search_opts:\n{raw_search_opts}\nand metadata:\n{raw_metadata}")

        if raw_search_opts:
            try:
                search_opts = dict(opt.split('=') for opt in raw_search_opts.split(','))
            except ValueError:
                return reply(search_error_message)

        else:
            search_opts = {}

        if raw_metadata:
            try:
                metadata = dict(opt.split('=') for opt in raw_metadata.split(','))
            except ValueError:
                return reply(search_error_message)
        else:
            metadata = {'owner_id': data.get('user')}

        self.log('DEBUG', f"{data['yas_hash']} final search_opts:\n{search_opts}\nand metadata:\n{metadata}")

        try:
            servers = self.server_manager.findall(metadata=metadata, **search_opts)
        except ServersFoundException as err:
            reply(f'There was an issue finding {search_opts}: {err}', thread=data['ts'])

        attachments = [self.parse_server_to_attachment(server.to_dict(), metadata) for server in servers]

        self.api_call('chat.postMessage',
                      channel=data['channel'],
                      thread_ts=data['ts'],
                      reply_broadcast=True,
                      attachments=attachments)

    def parse_server_to_attachment(self, server, metadata):

        self.log('DEBUG', f"Parsing server:\n{pformat(server)}")
        addresses = [interface['addr']
                     for network in server['addresses']
                     for interface in server['addresses'][network]]

        init = server['metadata'].get('init')
        test = server['metadata'].get('test')

        if init == 'done':
            if test == 'pass':
                attachment_color = '#7D7'
            elif test == 'full':
                attachment_color = '#AEC6CF'
            elif test == 'quick':
                attachment_color = '#AEC6CF'
            elif test == 'started':
                attachment_color = '#AEC6CF'
            elif test == 'fail':
                attachment_color = '#FF3'
            else:
                attachment_color = '#AAA'
        elif init == 'started':
            attachment_color = '#AEC6CF'
        elif init == 'fail':
            attachment_color = '#C23B22'
        else:
            attachment_color = '#AAA'

        for key in ['owner_id']:
            server['metadata'].pop(key, None)

        if 'owner_id' in metadata:
            # Add empty owner to remove from output
            metadata['owner'] = None

        fields = [dict(title=key, value=server['metadata'][key], short=True)
                  for key in server['metadata'] if not key in metadata and server['metadata'][key]]
        fields.append(dict(title='addresses', value=', '.join(addresses), short=len(addresses) == 1))
        fields.append(dict(title='id', value=server['id'], short=False))

        return dict(
            title=f"{server['name']}.{self.config.domain}",
            title_link=f"http://www.{server['name']}.{self.config.domain}",
            fields=fields,
            color=attachment_color)
