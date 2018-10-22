import version_compare
import name_expander

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
        spec = resp.content.decode('utf-8')
        names = name_expander.get_nvs(spec)
#        category_match = re.search('\W*Version[^:]*:(.+)', resp.content.decode('utf-8'))
#        # remove spaces
#        version = category_match.group(1).strip()
#        package_status = {'oma_pkg_ver': '%s' % (str(version)),
#                          'package': '%s' % (str(package))}
#        print('current version is: [{}]'.format(version))
#        print(package_status)
#        return version

check_version('htop')

#get_nvs(spec_path):
