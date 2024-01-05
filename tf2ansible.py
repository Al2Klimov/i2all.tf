import json
import sys

for resource in json.load(sys.stdin)['resources']:
    if resource['type'] == 'openstack_compute_instance_v2':
        for instance in resource['instances']:
            print('{name} ansible_host={access_ip_v4} ansible_user=centos'.format(**instance['attributes']))
