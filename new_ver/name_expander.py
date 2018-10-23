import rpm
import os
import sys
import tempfile
import requests
import json
import re

headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.2171.95 Safari/537.36'}

def get_nvs(spec):
    try:
       nvs = []
       ts = rpm.TransactionSet()
       rpm_spec = ts.parseSpec(spec)
       name = rpm.expandMacro("%{name}")
       version = rpm.expandMacro("%{version}")
       nvs.append(name)
       nvs.append(version)
       for (filename, num, flags) in rpm_spec.sources:
           if num == 0 and flags == 1:
               # prints htop.tar.gz
               tarball = filename.split("/")[-1]
               # full path
               # http://mirrors.n-ix.net/mariadb/mariadb-10.3.9/source/mariadb-10.3.9.tar.gz
               # print(filename)
               nvs.append(filename)
       return nvs
    except:
        return None


def check_version(package):
    url = "http://github.com/OpenMandrivaAssociation/{package}/raw/master/{package}.spec".format(package=package)
    resp = requests.get(url, headers=headers)
    temp = tempfile.NamedTemporaryFile(prefix=package, suffix=".spec")
    if resp.status_code == 404:
        print('requested package [{}] not found'.format(package))
    if resp.status_code == 200:
       spec = resp.content
       try:
           spec_path = temp.name
           # print("Created file is:", temp)
           # print("Name of the file is:", temp.name)
           temp.write(spec)
           temp.seek(0)
           names = get_nvs(spec_path)
           name = names[0]
           version = names[1]
           source0 = names[2]
#           print(name, version, source0)
           return name, version, source0
       finally:
           temp.close()

def github_check(upstream_url):
    split_url = upstream_url.split("/")[:-2]
#    print(split_url)
    project_url = '/'.join(split_url[:6]) + '/'
    try:
        apibase = 'https://api.github.com/repos' + '/' + split_url[3] + '/' +  split_url[4] + '/tags'
#        print(apibase)
        github_json = requests.get(apibase, headers=headers)
        data = github_json.json()
        project_name = (data[0]['name'])
#        print(project_name)
        category_match = re.search('\d+(?!.*/).*\d+', project_name)
        upstream_version = category_match.group(0)
        # good version here
#        print(upstream_version)
        return upstream_version, project_url
    except:
        apibase = 'https://api.github.com/repos' + '/' + split_url[3] + '/' +  split_url[4] + '/releases'
#        print(apibase)
        github_json = requests.get(apibase, headers=headers)
        data = github_json.json()
        project_name = (data[0]['name'])
        # 'start'
#        print(project_name)
        category_match = re.search('\d+(?!.*/).*\d+', project_name)
        upstream_version = category_match.group(0)
        # good version here
        print(upstream_version, project_url)
        return upstream_version, project_url

def check_upstream(package):
    upstream_name, our_ver, upstream_url = check_version(package)
    # htop 2.2.0 https://github.com/hishamhm/htop/archive/2.2.0.tar.gz
    print(upstream_name, our_ver, upstream_url)
    if 'github' in upstream_url:
        github_check(upstream_url)
#        try:
#        split_url = upstream_url.split("/")[:-2]
#        print(split_url)
#        project_url = '/'.join(split_url[:6]) + '/'
#        try:
#            apibase = 'https://api.github.com/repos' + '/' + split_url[3] + '/' +  split_url[4] + '/tags'
#            print(apibase)
#            github_json = requests.get(apibase, headers=headers)
#            data = github_json.json()
#            project_name = (data[0]['name'])
#            print(project_name)
#            category_match = re.search('\d+(?!.*/).*\d+', project_name)
#            upstream_version = category_match.group(0)
#            # good version here
#            print(upstream_version)
#            return upstream_version, project_url
#        except:
#            apibase = 'https://api.github.com/repos' + '/' + split_url[3] + '/' +  split_url[4] + '/releases'
#            print(apibase)
#            github_json = requests.get(apibase, headers=headers)
#            data = github_json.json()
#            project_name = (data[0]['name'])
#            print(project_name)
#            category_match = re.search('\d+(?!.*/).*\d+', project_name)
#            upstream_version = category_match.group(0)
#            # good version here
#            print(upstream_version)
#            return upstream_version, project_url

    #        except:
    #            return None


#version = get_nvs('/home/omv/mariadb/mariadb.spec')

#check_upstream("fuse")
#check_github('https://api.github.com/repos/hishamhm/htop/tags', 'htop')
#print(version)
# name
#print(version[0])
# version
#print(version[1])
# source0
#print(version[2])
