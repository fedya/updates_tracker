#!/usr/bin/python
import requests

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def check_package(package):
    url = "http://github.com/OpenMandrivaAssociation/{package}/raw/master/{package}.spec".format(package=package)

    resp = requests.get(url, headers=headers)
    if resp.status_code == 404:
        print('requested package [{}] not found'.format(package))
    # page exist
    if resp.status_code == 200:
        print('requested package [{}] found'.format(package))
        print('trying to detect current version')
#    print(resp.status_code)
#    print(resp.content)

check_package('stunnel')
