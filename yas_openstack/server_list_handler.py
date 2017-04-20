from yas_openstack.openstack_handler import OpenStackHandler
from yas_openstack.server import ServersFoundException

# {
#     "attachments": [
#         {
#             "title": "www.fooey.cloud.rf29.net/",
#             "title_link": "http://www.fooey.cloud.rf29.net/",
#             "fields": [
#                 {
#                     "title": "init",
#                     "value": "<https://jenkins.prod.rf29.net/view/Openstack/job/CloudInit/500/|Complete>",
#                     "short": true
#                 },
#                 {
#                     "title": "branch: ",
#                     "value": "<github.com/refinery29/dash-dam/pull/183|dash-dam:new-examples-dir>",
#                     "short": true
#                 },
#                 {
#                     "title": "image name",
#                     "value": "1490904773",
#                     "short": true
#                 },
#                 {
#                     "title": "image creation date",
#                     "value": "2017-03-28T16:47:20Z",
#                     "short": true
#                 }
#             ],
#             "image_url": "http://my-website.com/path/to/image.jpg"
#         }
#     ]
# }

class OpenStackServerListHandler(OpenStackHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(r'(?:list)\ ?([a-z\.=,:]+)?(?:\ fields\ )?([\-a-zA-Z0-9\,_]+)?', *args, **kwargs)

    def handle(self, data, reply):
        search_opts, result_fields = self.current_match.groups()
        self.log('DEBUG',
                 f"Parsed from {data['yas_hash']} search_opts:\n{search_opts}\nand result_fields:\n{result_fields}")

        if search_opts:
            try:
                search_opts = dict(opt.split(':') for opt in search_opts.split(' '))
            except ValueError:
                reply('Invalid search opts, list query must look like: '
                      '"list[ <sort query>: <argument>[ <query>: <argument>[ ...]][ fields <field1>[,<fieldN>]]"\n'
                      'For example:\n&gt; list name=foobar fields metadata,created\n'
                      'Available sort queries and fields may be found in the '
                      # pylint: disable=line-too-long
                      '<https://developer.openstack.org/api-ref/compute/?expanded=list-servers-detailed-detail#list-servers-detailed|docs>.')
                return

        else:
            search_opts = {}

        if result_fields:
            result_fields_list = result_fields.split(',')
        else:
            result_fields_list = self.config.default_list_result_fields

        reply(f"Preparing listing of {search_opts or 'all'} with {result_fields_list}", thread=data['ts'])

        try:
            servers = self.server_manager.findall(**search_opts)
        except ServersFoundException as err:
            reply(f'There was an issue finding {search_opts}: {err}', thread=data['ts'])

        self.log('INFO', f'parsing {len(servers)} servers...')

        servers = [server.to_dict() for server in servers]

        server_info = {}

        for server in servers:
            server_id = server.get('id')
            server_info[server_id] = {}
            if 'addresses' in result_fields_list:
                server_info[server_id]['addresses'] = [interface['addr']
                                                       for provider in server['addresses']
                                                       for interface in server['addresses'][provider]]
                result_fields_list.remove('addresses')
            if '_addresses' in result_fields_list:
                result_fields_list.remove('_addresses')
                result_fields_list.append('addresses')
            for field in result_fields_list:
                server_info[server_id][field] = server[field]

        self.api_call('chat.postMessage',
                      channel=data['channel'],
                      thread_ts=data['ts'],
                      reply_broadcast=True,
                      attachments=server_info)
