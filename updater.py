#!/usr/bin/python

import argparse
import requests
import os
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
        if "github|gitlab"  in str(upstream_url):
            # split url and rejoin
            split_url = upstream_url.split("/")[:-2]
            basename = '/'.join(split_url[:3]) + '/'
            project_name = '/'.join(split_url[:5]) + '/'
            cmd = 'git ls-remote --tags --refs %s' % (project_name)
            proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_list = proc.communicate()[0]
            version_list = []
            #category_match = re.finditer("\d+(?!.*/).*\d+", stdout_list.decode('utf-8'))
            category_match = re.finditer(".*\/v?.*?([0-9.]+).*", stdout_list.decode('utf-8'))
            for match in category_match:
                version_list.append(match[1])
            upstream_version = max(version_list)
            print("upstream version : [%s]" % upstream_version)
            return upstream_version
        else:
            print("not ready yet")
            exit(0)

def compare_versions(package):
    our_ver = check_version(package)
    they_ver = check_upstream(package)
    if sorted(set(str(our_ver))) == sorted(set(str(they_ver))):
        print("OpenMandriva version of [{0}] is same [{1}] as in upstream [{2}]".format(package, our_ver, they_ver))
    elif sorted(set(str(our_ver))) < sorted(set(str(they_ver))):
        print("OpenMandriva version of [{0}] is lower [{1}] than in upstream [{2}]".format(package, our_ver, they_ver))
    else:
        print("OpenMandriva version of [{0}] is newer [{1}] than in upstream [{2}]".format(package, our_ver, they_ver))


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

#check_upstream("libarchive")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", help="package to check",
                    type=compare_versions,
                    action="store")

    args = parser.parse_args()
