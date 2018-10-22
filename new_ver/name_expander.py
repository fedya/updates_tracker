import rpm
import os
import sys

def get_nvs(spec):
    try:
       nvs = []
       ts = rpm.TransactionSet()
       rpm_spec = ts.parseSpec(spec)
       name = rpm.expandMacro("%{name}")
       version = rpm.expandMacro("%{version}")
       nvs.append(name)
       nvs.append(version)
       print(name)
       print(name)
       print(name)
       print(name)
       print(name)
       for (filename, num, flags) in rpm_spec.sources:
           if num == 0 and flags == 1:
               # prints htop.tar.gz
               tarball = filename.split("/")[-1]
               # full path
               # http://mirrors.n-ix.net/mariadb/mariadb-10.3.9/source/mariadb-10.3.9.tar.gz
               # print(filename)
               nvs.append(filename)
       print(nvs)
       return nvs
    except:
        return None

#version = get_nvs('/home/omv/mariadb/mariadb.spec')
# name
#print(version[0])
# version
#print(version[1])
# source0
#print(version[2])
