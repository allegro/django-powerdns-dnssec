from pkg_resources import working_set, Requirement


try:
    req = Requirement.parse('django-powerdns-dnssec')
    VERSION = working_set.find(req).version
except AttributeError:
    import json
    with open('version.json') as f:
        VERSION = '.'.join(str(part) for part in json.load(f))
