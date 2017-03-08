from facade.openstack import Client, ServerCreationDefaults


FILE_NAME = 'etc/yas/yas.yml'

PARAMETERS = dict(
    compute_version='2.38',
    username=None,
    password=None,
    project_name=None,
    auth_url='http://keystone:5000',
    project_domain_name='default',
    user_domain_name='default',
    create_server_defaults={
        image_name=client._novaclient.glance.find_image('ubuntu/trusty64'),
        flavor_name=client._novaclient.flavors.find(name='m1.big').id,
        # TODO requires neutron client
        nics=[{
            "net-id": '832bbfef-7ebd-4da5-8029-f7cf89e4ee5e',
            "v4-fixed-ip": ''
        }],
        security_groups=None,
        userdata=None,
        key_name=None
    }
)
