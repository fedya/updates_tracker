import name_expander

import argparse
import requests
import os
import json
import subprocess
import re
import tempfile

def tryint(x):
    try:
        return int(x)
    except ValueError:
        return x

def splittedname(s):
    return tuple(tryint(x) for x in re.split('([0-9]+)', s))

def compare_versions(package):
    name, our_ver, source0 = name_expander.check_version(package)
    upstream_ver, project_url = name_expander.check_upstream(package)

    package_item = {
        'package': package,
        'omv_version': our_ver,
        'upstream_version': upstream_ver,
        'project_url': project_url
    }

    if splittedname(our_ver) == splittedname(upstream_ver):
        package_item['status'] = 'no updates required'
    if splittedname(our_ver) < splittedname(upstream_ver):
        package_item['status'] = 'outdated'
    if splittedname(our_ver) > splittedname(upstream_ver):
        package_item['status'] = 'omv version is newer'

    print(package_item)
    return package_item

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', nargs='+', type=compare_versions)
    args = parser.parse_args()
    print(json.dumps({"package": args.package}))
