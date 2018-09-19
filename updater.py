#!/usr/bin/python

import argparse
import requests
import os
import json
import subprocess
import re

headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.2171.95 Safari/537.36'}

def check_version(package):
    url = "http://github.com/OpenMandrivaAssociation/{package}/raw/master/{package}.spec".format(package=package)
    resp = requests.get(url, headers=headers)
    if resp.status_code == 404:
        print('requested package [{}] not found'.format(package))
    if resp.status_code == 200:
        category_match = re.search('\W*Version[^:]*:(.+)', resp.content.decode('utf-8'))
        # remove spaces
        version = category_match.group(1).strip()
        package_status = {'oma_pkg_ver': '%s' % (str(version)),
                          'package': '%s' % (str(package))}
        print('current version is: [{}]'.format(version))
        print(package_status)
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
        print(upstream_url)
        print('source0 is: {}'.format(upstream_url))
        if 'github' in upstream_url:
            split_url = upstream_url.split("/")[:-2]
            project_url = '/'.join(split_url[:6]) + '/'
            apibase = 'https://api.github.com/repos' + '/' + split_url[3] + '/' +  split_url[4] + '/tags'
            print(apibase)
            github_json = requests.get(apibase, headers=headers)
            data = github_json.json()
            project_name = (data[0]['name'])
            print(project_name)
            category_match = re.search('\d+(?!.*/).*\d+', project_name)
            upstream_version = category_match.group(0)
#            print(upstream_version)
            return upstream_version, project_url
        elif 'freedesktop' in str(upstream_url):
            split_url = upstream_url.split("/")[:6]
            project_url = '/'.join(split_url[:6]) + '/'
            freedesktop_req = requests.get(project_url, headers=headers, allow_redirects=True)
            version_list = []
            if freedesktop_req.status_code == 404:
                print('requested url [{}] not found'.format(url))
            if freedesktop_req.status_code == 200:
                if 'x11-driver' in package:
                    split_name = package.split("-")[:4]
                    xf86base = 'xf86-' + (split_name[2]) + '-' + (split_name[3])
                    print(xf86base)
                    category_match = re.finditer(xf86base+'[-]([\d.]*\d+)', freedesktop_req.content.decode('utf-8'))
                    for match in category_match:
                        version_list.append(match[1])
                    upstream_max_version= max([[int(j) for j in i.split(".")] for i in version_list])
                    upstream_version = ".".join([str(i) for i in upstream_max_version])
                    return upstream_version, project_url
                else:
                    category_match = re.finditer(package+'[-]([\d.]*\d+)', freedesktop_req.content.decode('utf-8'))
                    for match in category_match:
                        version_list.append(match[1])
#                        print(match.group(1))
                    upstream_max_version= max([[int(j) for j in i.split(".")] for i in version_list])
                    upstream_version = ".".join([str(i) for i in upstream_max_version])
                    return upstream_version, project_url
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', nargs='+', type=compare_versions)
    parser.add_argument("-f", "--file", help="Open specified file")
    args = parser.parse_args()
#    PackageFile = args.file
#    with open(PackageFile) as f:
#        data = f.readlines()
#        final_list = []
#        for pkg in data:
#            final_list.append(pkg.strip())
#        pkg_list = ' '.join(final_list)
#        print(pkg_list)

    print(json.dumps({"package": args.package}))
