import json
import sys


def infloop(it):
    while True:
        yield from it


hierarchy = {'agent': 'sat', 'sat': 'master'}
maxnodes = {'agent': 1}
unzoned = {}
zones = {}

for (child, parent) in hierarchy.items():
    unzoned[child] = set()
    unzoned[parent] = set()

for resource in json.load(sys.stdin)['resources']:
    if resource['type'] == 'openstack_compute_instance_v2':
        for instance in resource['instances']:
            print('''object Endpoint "{name}" {{
\thost = "{access_ip_v4}"
}}'''.format(**instance['attributes']))

            name = instance['attributes']['name']

            haystack: set
            for (kind, haystack) in unzoned.items():
                if kind + '-' in name:
                    haystack.add(name)
                    break

haystack: set
for (kind, haystack) in unzoned.items():
    m = maxnodes.get(kind) or 2
    zones[kind] = zz = {}
    zone = []

    while haystack:
        zone.append(haystack.pop())

        if len(zone) >= m or not haystack:
            zz['+'.join(zone)] = zone
            zone = []

zz: dict
for (kind, zz) in zones.items():
    parents = {}
    step = kind

    while not parents and step in hierarchy:
        step = hierarchy[step]
        parents = zones[step]

    if not parents:
        parents[''] = []

    parents = infloop(parents)

    for (name, endpoints) in zz.items():
        print('''object Zone "{}" {{
\tendpoints = [ "{}" ]
\tparent = "{}"
}}'''.format(name, '", "'.join(endpoints), next(parents)))
