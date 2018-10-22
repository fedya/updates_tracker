import rpm
import os
import sys
import tempfile
import requests

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
    headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.2171.95 Safari/537.36'}
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
           print(name, version, source0)
           return name, version, source0
       finally:
           temp.close()

#version = get_nvs('/home/omv/mariadb/mariadb.spec')
#print(version)
# name
#print(version[0])
# version
#print(version[1])
# source0
#print(version[2])
