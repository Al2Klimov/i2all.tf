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
}}
object Host "{name}" {{ }}'''.format(**instance['attributes']))

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

print('''
template Host default {
\tcheck_command = "check_random.py"
\tvars.random_limit = 10
\tvars.random_warning = 6
\tvars.random_critical = 7
\tvars.random_unknown = 8

\tfor (z in get_objects(Zone)) {
\t\tif (name in z.endpoints) {
\t\t\tzone = z.parent || z.name
\t\t\tvars.service_zone = if (name.contains("agent-")) { z.parent } else { z.name }
\t\t\tbreak
\t\t}
\t}
}

apply Service "memory-usage" {
\tcheck_command = "memory-usage"
\tzone = host.vars.service_zone
\tcommand_endpoint = host.name
\tassign where true
}

object CheckCommand "check_random.py" {
\tcommand = [ "python3", PluginDir + "/check_random.py" ]

\targuments = {
\t\t"-l" = "$random_limit$"
\t\t"-w" = "$random_warning$"
\t\t"-c" = "$random_critical$"
\t\t"-u" = "$random_unknown$"
\t}
}

object CheckCommand "memory-usage" {
\tcommand = [ "python3", "/opt/Linuxfabrik/monitoring-plugins/check-plugins/memory-usage/memory-usage" ]
}''')
