import rpm
import os
import sys
import tempfile
import requests
import json
import re

github_headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.2171.95 Safari/537.36',
                  'Authorization': 'token from_github'}
headers = {
    'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.2171.95 Safari/537.36'}


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
                # path
                # http://mirrors.n-ix.net/mariadb/mariadb-10.3.9/source/
                source_link = '/'.join(filename.split("/")[:-1])
                nvs.append(source_link)
        return nvs
    except:
        return None


def check_version(package):
    #url = "http://github.com/OpenMandrivaAssociation/{package}/raw/master/{package}.spec".format(package=package)
    url = "https://abf.io/import/{package}/raw/rosa2019.1/{package}.spec".format(
        package=package)
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
#           print(source0)
#           print(name, version, source0)
            return name, version, source0
        except:
            return name, version, '0'
        finally:
            temp.close()


def github_check(upstream_url):
    # add here version list
    split_url = upstream_url.split("/")[:-1]
    project_url = '/'.join(split_url[:6]) + '/'
    try:
        apibase = 'https://api.github.com/repos' + '/' + \
            split_url[3] + '/' + split_url[4] + '/tags'
        print(apibase)
        github_json = requests.get(apibase, headers=github_headers)
        data = github_json.json()
        project_name = (data[0]['name'])
        if 'xf86' in project_url:
            print("imhere")
            category_match = re.search('[-]([\d.]*\d+)', project_name)
            upstream_version = category_match.group(1)
            print(upstream_version)
        else:
            category_match = re.search('\d+(?!.*/).*\d+', project_name)
            upstream_version = category_match.group(0)
            print(upstream_version)
        return upstream_version, project_url
    except:
        apibase = 'https://api.github.com/repos' + '/' + \
            split_url[3] + '/' + split_url[4] + '/releases'
#        print(apibase)
        github_json = requests.get(apibase, headers=github_headers)
        data = github_json.json()
        project_name = (data[0]['name'])
        # 'start'
#        print(project_name)
        category_match = re.search('\d+(?!.*/).*\d+', project_name)
        upstream_version = category_match.group(1)
        # good version here
        print(upstream_version, project_url)
        return upstream_version, project_url


def freedesktop_check(upstream_url, package):
    split_url = upstream_url.split("/")[:6]
    project_url = '/'.join(split_url[:6]) + '/'
    print(project_url)
    freedesktop_req = requests.get(
        project_url, headers=headers, allow_redirects=True)
    version_list = []
    if freedesktop_req.status_code == 404:
        print('requested url [{}] not found'.format(upstream_url))
    if freedesktop_req.status_code == 200:
        if 'x11-driver' in package:
            split_name = package.split("-")[:4]
            xf86base = 'xf86-' + (split_name[2]) + '-' + (split_name[3])
            category_match = re.finditer(
                xf86base+'[-]([\d.]*\d+)', freedesktop_req.content.decode('utf-8'))
            for match in category_match:
                version_list.append(match[1])
            upstream_max_version = max(
                [[int(j) for j in i.split(".")] for i in version_list])
            upstream_version = ".".join([str(i) for i in upstream_max_version])
            return upstream_version, project_url
        elif 'server' in package:
            pkg_notcare = re.compile(
                'xorg-server'+'[-]([\d.]*\d+)', re.IGNORECASE)
            category_match = re.finditer(
                pkg_notcare, freedesktop_req.content.decode('utf-8'))
            for match in category_match:
                version_list.append(match[1])
            upstream_max_version = max(
                [[int(j) for j in i.split(".")] for i in version_list])
            upstream_version = ".".join([str(i) for i in upstream_max_version])
            print(upstream_version, project_url)
            return upstream_version, project_url

        elif 'x11-driver' not in package:
            pkg_notcare = re.compile(package+'[-]([\d.]*\d+)', re.IGNORECASE)
            category_match = re.finditer(
                pkg_notcare, freedesktop_req.content.decode('utf-8'))
            for match in category_match:
                version_list.append(match[1])
            upstream_max_version = max(
                [[int(j) for j in i.split(".")] for i in version_list])
            upstream_version = ".".join([str(i) for i in upstream_max_version])
            print(upstream_version, project_url)
            return upstream_version, project_url


def any_other(upstream_url, package):
    split_url = upstream_url.split("/")[:6]
    project_url = '/'.join(split_url[:5])
    print(split_url)
    print(project_url)
    req = requests.get(project_url, headers=headers, allow_redirects=True)
    version_list = []
    if req.status_code == 404:
        print('requested url [{}] not found'.format(upstream_url))
    if req.status_code == 200:
        try:
            pkg_notcare = re.compile(package+'[-]([\d.]*\d+)', re.IGNORECASE)
            category_match = re.finditer(
                pkg_notcare, req.content.decode('utf-8'))
            for match in category_match:
                version_list.append(match[1])
            upstream_max_version = max(
                [[int(j) for j in i.split(".")] for i in version_list])
            upstream_version = ".".join([str(i) for i in upstream_max_version])
            print(upstream_version, project_url)
            return upstream_version, project_url
        except:
            category_match = re.finditer(
                'href=[\'"]?([\d.]*\d+)', req.content.decode('utf-8'))
            for match in category_match:
                version_list.append(match[1])
            upstream_max_version = max(
                [[int(j) for j in i.split(".")] for i in version_list])
            upstream_version = ".".join([str(i) for i in upstream_max_version])
            print(upstream_version, project_url)
            return upstream_version, project_url


def qt5_check(upstream_url):
    split_url = upstream_url.split("/")[:6]
    project_url = '/'.join(split_url[:5])
    req = requests.get(project_url, headers=headers, allow_redirects=True)
    version_list = []
    # http://download.qt.io/official_releases/qt/5.11/
    true_version_list = []
    if req.status_code == 404:
        print('requested url [{}] not found'.format(upstream_url))
    if req.status_code == 200:
        try:
            first_url = re.finditer(
                'href=[\'"]?([\d.]*\d+)', req.content.decode('utf-8'))
            for match in first_url:
                version_list.append(match[1])
            upstream_max_version = max(
                [[int(j) for j in i.split(".")] for i in version_list])
            upstream_version = ".".join([str(i) for i in upstream_max_version])

            new_url = project_url + '/' + upstream_version
            print(new_url)
            req2 = requests.get(new_url, headers=headers, allow_redirects=True)
            if req2.status_code == 404:
                print('requested url [{}] not found'.format(new_url))
            if req2.status_code == 200:
                try:
                    pkg_ver = re.finditer(
                        'href=[\'"]?([\d.]*\d+)', req2.content.decode('utf-8'))
                    for match in pkg_ver:
                        true_version_list.append(match[1])
                    upstream_max_version = max(
                        [[int(j) for j in i.split(".")] for i in true_version_list])
                    upstream_version = ".".join(
                        [str(i) for i in upstream_max_version])
                    print(upstream_version)
                    return upstream_version, project_url
                except:
                    return
        except:
            return


def check_python_module(package):
    try:
        split_name = package.split("-")[1]
        url = 'https://pypi.python.org/pypi/{}/json'.format(split_name)
        req = requests.get(url, headers=headers, allow_redirects=True)
        pypi_json = requests.get(url, headers=headers)
        data = pypi_json.json()
        upstream_version = data['info']['version'][:]
        project_url = data['info']['project_url'][:]
        print(upstream_version, project_url)
        return upstream_version, project_url
    except:
        return


def netfilter_check(package):
    url = 'https://www.netfilter.org/news.html'
    version_list = []
    try:
        req = requests.get(url, allow_redirects=True)
        pkg_notcare = re.compile(package+'[-]([\d.]*\d+)', re.IGNORECASE)
        category_match = re.finditer(pkg_notcare, req.content.decode('utf-8'))
        for match in category_match:
            version_list.append(match[1])
        upstream_max_version = max(
            [[int(j) for j in i.split(".")] for i in version_list])
        upstream_version = ".".join([str(i) for i in upstream_max_version])
        print(upstream_version, url)
        return upstream_version, url
    except:
        return


def check_upstream(package):
    upstream_name, our_ver, upstream_url = check_version(package)
    # htop 2.2.0 https://github.com/hishamhm/htop/archive/2.2.0.tar.gz
    print(upstream_name, our_ver, upstream_url)
    if 'github' in upstream_url:
        return github_check(upstream_url)
    elif 'freedesktop' in upstream_url:
        return freedesktop_check(upstream_url, package)
    elif 'qt.io' in upstream_url:
        return qt5_check(upstream_url)
    elif 'pypi' in upstream_url:
        return check_python_module(package)
    elif 'pythonhosted' in upstream_url:
        return check_python_module(package)
    elif 'netfilter' in upstream_url:
        return netfilter_check(package)
    else:
        return any_other(upstream_url, package)
    if '0' in upstream_url:
        print("no source0 detected")


# version = get_nvs('/home/omv/mariadb/mariadb.spec')

# check_upstream("x11-driver-video-sisimedia")
# check_upstream("iptables")
# check_github('https://api.github.com/repos/hishamhm/htop/tags', 'htop')
# print(version)
# name
# print(version[0])
# version
# print(version[1])
# source0
# print(version[2])
