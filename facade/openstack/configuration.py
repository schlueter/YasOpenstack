DIRECTORIES = [
    '/usr/local/etc/yas/handler_configs',
    '/usr/local/etc/handler_configs',
    '/etc/yas/handler_configs',
    '/etc/handler_configs'
]

FILE_NAME = 'openstack.yml'

PARAMETERS = dict(
    compute_version='2.38',
    project_domain_name='default',
    user_domain_name='default',
    username=None,
    password=None,
    project_name=None,
    auth_url=None,
    create_server_defaults=dict(
        image_name=ubuntu/trusty64,
        flavor_name=m1.big,
        # TODO requires neutron client
        nics='auto',
        security_groups=[],
        userdata=None,
        key_name=''
    )
)


