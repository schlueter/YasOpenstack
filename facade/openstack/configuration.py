FILE_NAME = 'etc/yas/openstack.yml'

PARAMETERS = dict(
    compute_version='2.38',
    auth_url='http://your.keystone:5000',
    project_domain_name='default',
    user_domain_name='default',
    project_name=None,
    username=None,
    password=None,
    auth_url=None,
    create_server_defaults=dict(
        image_name='ubuntu/trusty64',
        flavor_name='m1.big',
        nics='auto',
        security_groups=[],
        userdata=None,
        key_name=''
    )
)