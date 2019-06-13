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
    try:

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
        return package_item
    except:
        return None


if __name__ == '__main__':
    weird_list = []
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', nargs='+', type = compare_versions)
    parser.add_argument('--file', help='file with packages list')
    parser.add_argument('--output', help='file to output results')
    args = parser.parse_args()
    if args.file is not None:
        with open(args.file) as file:
            try:
                for line in file:
                    a = compare_versions(line.strip())
                    weird_list.append(a)
            except:
                print('shit happened')
        if args.output is not None:
            with open(args.output, 'w') as out_json:
                json.dump({'packages': weird_list}, out_json, sort_keys=True, indent=4)
        else:
            print(json.dumps({"packages": weird_list}))
    if args.package is not None:
        packages = [i for i in args.package if i is not None]
        print(json.dumps({"packages": packages}))
