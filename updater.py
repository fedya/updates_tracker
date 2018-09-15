#!/usr/bin/python

import argparse
import requests
import os
import json
import subprocess
import re

headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def check_version(package):
    url = "http://github.com/OpenMandrivaAssociation/{package}/raw/master/{package}.spec".format(package=package)
    resp = requests.get(url, headers=headers)
    if resp.status_code == 404:
        print('requested package [{}] not found'.format(package))
    # page exist
    if resp.status_code == 200:
        print('requested package [{}] found'.format(package))
        print('trying to detect current version')
        category_match = re.search('\W*Version[^:]*:(.+)', resp.content.decode('utf-8'))
        # remove spaces
        version = category_match.group(1).strip()
        package_status = {'oma_pkg_ver': '%s' % (str(version)),
                          'package': '%s' % (str(package))}
        print('current version is: [{}]'.format(version))
        return version

def check_upstream(package):
    url = "http://github.com/OpenMandrivaAssociation/{package}/raw/master/{package}.spec".format(package=package)
    resp = requests.get(url, headers=headers)
    if resp.status_code == 404:
        print('requested url [{}] not found'.format(url))
    if resp.status_code == 200:
        category_match = re.search('\Source0[^:]*:(.+)', resp.content.decode('utf-8'))
        # to complicated regex here, just split -
        upstream_url = category_match.group(1).strip()
        # print('source0 is: {}'.format(upstream_url))
        rgx = re.compile(r'git[hl]')
        if rgx.search(upstream_url):
            split_url = upstream_url.split("/")[:-2]
            project_url = '/'.join(split_url[:5]) + '/'
            apibase = 'https://api.github.com/repos' + '/' + split_url[3] + '/' +  split_url[4] + '/tags'
            github_json = requests.get(apibase, headers=headers)
            data = github_json.json()
            project_name = (data[0]['name'])
            version_list = []
            category_match = re.search('\d+(?!.*/).*\d+', project_name)
            upstream_version = category_match.group(0)
            return upstream_version, project_url
            # return {'upstream_version': upstream_version, 'project_url': project_url}
        else:
            print("not ready yet")
            exit(0)

def tryint(x):
    try:
        return int(x)
    except ValueError:
        return x

def splittedname(s):
    return tuple(tryint(x) for x in re.split('([0-9]+)', s))

def compare_versions(package):
    our_ver = check_version(package)
    upstream_ver, project_url = check_upstream(package)
    a = splittedname(our_ver)
    b = splittedname(upstream_ver)

    data = {}
    data['packages'] = []
    data['packages'].append({
    'package': package,
    'omv_version': our_ver,
    'upstream_version': upstream_ver,
    'project_url': project_url
    })
    dumper = json.dumps(data)
    print(dumper)

    if splittedname(our_ver) == splittedname(upstream_ver):
        print("OpenMandriva version of [{0}] is same [{1}] as in upstream [{2}]".format(package, our_ver, upstream_ver))
        print("Upstream URL {0}".format(project_url))
    elif splittedname(our_ver) < splittedname(upstream_ver):
        print("OpenMandriva version of [{0}] is lower [{1}] than in upstream [{2}]".format(package, our_ver, upstream_ver))
        print("Upstream URL {0}".format(project_url))
    elif splittedname(our_ver) > splittedname(upstream_ver):
        print("OpenMandriva version of [{0}] is newer [{1}] than in upstream [{2}]".format(package, our_ver, upstream_ver))
        print("Upstream URL {0}".format(project_url))

def check_upstream_stunnel():
    url = "http://www.stunnel.org/downloads.html"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 404:
        print('requested url [{}] not found'.format(url))
    if resp.status_code == 200:
        category_match = re.search('[-][0-9]*[.,][0-9]*', resp.content.decode('utf-8'))
        # to complicated regex here, just split -
        upstream_version = category_match.group(0).strip('-')
        print('upstream version is: [{}]'.format(upstream_version))
        return upstream_version

#check_upstream("stunnel")
#compare_versions("stunnel")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", help="package to check",
                    type=compare_versions,
                    action="store")

    args = parser.parse_args()
