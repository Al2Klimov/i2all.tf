import json
import sys


def infloop(it):
    while True:
        yield from it


hierarchy = {'agent': 'sat', 'sat': 'master'}
maxnodes = {'agent': 1}
services = {'agent': 1000, 'sat': 4000, 'master': 16000}
unzoned = {}
zones = {}

for (child, parent) in hierarchy.items():
    unzoned[child] = {}
    unzoned[parent] = {}

for resource in json.load(sys.stdin)['resources']:
    if resource['type'] == 'openstack_compute_instance_v2':
        for instance in resource['instances']:
            name = instance['attributes']['name']

            for (kind, haystack) in unzoned.items():
                if kind + '-' in name:
                    haystack[name] = instance['attributes']
                    haystack[name]['services'] = services[kind]
                    break

haystack: dict
for (kind, haystack) in unzoned.items():
    m = maxnodes.get(kind) or 2
    zones[kind] = zz = {}
    zone = []

    while haystack:
        (name, attrs) = haystack.popitem()
        zone.append(name)

        print('''object Endpoint "{name}" {{
\thost = "{access_ip_v4}.nip.io"
}}
globals.ServicesPerHost["{name}"] = {services}
object Host "{name}" {{ }}'''.format(**attrs))

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
\t\t\tvar serviceZones = [ vars.service_zone ]

\t\t\twhile (true) {
\t\t\t\tvar z = get_object(Zone, serviceZones[len(serviceZones) - 1])

\t\t\t\tif (!z.parent) {
\t\t\t\t\tbreak
\t\t\t\t}

\t\t\t\tserviceZones.add(z.parent)
\t\t\t}

\t\t\tbreak
\t\t}
\t}

\tfor (z in get_objects(Zone)) {
\t\tif (NodeName in z.endpoints) {
\t\t\tvars.apply_services = z.name in serviceZones
\t\t\tbreak
\t\t}
\t}
}

apply Service "memory-usage" {
\tcheck_command = "memory-usage"
\tzone = host.vars.service_zone
\tcommand_endpoint = host.name
\tassign where host.vars.apply_services
}

apply Service "load" {
\tcheck_command = "Lf-load"
\tzone = host.vars.service_zone
\tcommand_endpoint = host.name
\tassign where host.vars.apply_services
}

apply Service "check_random.py:" for (i in range(ServicesPerHost[host.name])) {
\tcheck_command = "check_random.py"
\tzone = host.vars.service_zone
\tcommand_endpoint = host.name
\tassign where host.vars.apply_services
}

apply ScheduledDowntime "" for (i in range(1)) to Service {
\tauthor = "icingaadmin"
\tcomment = "// TODO"
\tzone = service.zone

\tranges = {
\t\t"monday - sunday" = "00:00-24:00"
\t}

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
}

object CheckCommand "Lf-load" {
\tcommand = [ "python3", "/opt/Linuxfabrik/monitoring-plugins/check-plugins/load/load" ]
}

template InfluxdbWriter default {
\tenable_ha = true
}''')
