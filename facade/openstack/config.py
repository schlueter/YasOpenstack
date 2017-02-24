from facade.openstack import Client, ServerCreationDefaults


client = Client()

server_creation_defaults = ServerCreationDefaults(
    image=client._novaclient.glance.find_image('ubuntu/trusty64'),
    flavor=client._novaclient.flavors.find(name='m1.big').id,
    # TODO requires neutron client
    security_groups=['344188ea-7747-4a67-8517-743e99799fda'],
    userdata='',
    key_name='bs',
    # TODO requires neutron client
    nics=[{
        "net-id": '832bbfef-7ebd-4da5-8029-f7cf89e4ee5e',
        "v4-fixed-ip": ''
    }]
)
