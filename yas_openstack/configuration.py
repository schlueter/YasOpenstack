FILE_NAME = 'etc/yas/openstack.yml'

PARAMETERS = dict(
    compute_version='2.38',
    auth_url='http://your.keystone:5000',
    project_domain_name='default',
    user_domain_name='default',
    project_name=None,
    username=None,
    password=None,
    create_server_defaults=dict(
        image_name='default',
        flavor_name='default',
        nics='auto',
        security_groups=[],
        userdata=None,
        key_name=''
    )
)
