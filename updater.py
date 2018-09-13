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
#        print(package_status)
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
        #print('source0 is: {}'.format(upstream_url))
        if "github" or "gitlab" in upstream_url:
            # split url and rejoin
            split_url = upstream_url.split("/")[:-2]
            basename = '/'.join(split_url[:3]) + '/'
            project_name = '/'.join(split_url[:5]) + '/'
            print(project_name)
            cmd = 'git ls-remote --tag %s' % (project_name)
            proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_list = proc.communicate()[0]
            category_match = re.search("refs/tags/(.*)$", stdout_list.decode('utf-8'))
            obtained_ver = category_match.group(1)
            if "v" in obtained_ver:
                split_ver = obtained_ver.split("v")
                print(split_ver[1])
            else:
                print(obtained_ver)
        else:
            print("not ready yet")

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

def check_package(package):
    check_version(package)
    check_upstream(package)
#    check_upstream_stunnel()

#check_package('htop')
#check_version('htop')
#check_upstream_stunnel()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", help="package to check",
                    type=check_package,
                    action="store")

    args = parser.parse_args()
