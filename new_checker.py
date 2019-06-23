#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rpm
import os
import sys
import tempfile
import requests
import json
import re
import subprocess
import shutil
import argparse

github_headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.2171.95 Safari/537.36',
                  'Authorization': 'token github_token'}
headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.2171.95 Safari/537.36'}

home = os.environ.get('HOME')
project_version = 'master'
nvs = []
nvss =  []

def get_nvs(spec):
    print('extracting OMV version first')
    try:
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
                nvs.append(filename)
        # returns
        # ['vim', '8.1.1524', 'https://github.com/vim/vim/archive', 'https://github.com/vim/vim/archive/v8.1.1524.tar.gz']
        print('omv version: [{}]'.format(version))
        print('omv package name: [{}]'.format(name))
    except:
        print('probablt specfile damaged')
        return None


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
#        print(upstream_version, project_url)
        return upstream_version, project_url


def check_python_module(package):
    try:
        print('im in check python mod')
        name, omv_version, url, source0 = check_version(package)
        print(name)
        split_name = re.split(r'python([\d]?)-', name)[-1]
        print(split_name)
        url = 'https://pypi.python.org/pypi/{}/json'.format(split_name)
        print(url)
        req = requests.get(url, allow_redirects=True)
        if req.status_code == 404:
            print('requested module [{}] not found'.format(split_name))
            url = 'https://pypi.python.org/pypi/{}/json'.format(package)
            req = requests.get(url, allow_redirects=True)

            if req.status_code == 404:
                split_name = 'py' + name.split("-")[1]
                url = 'https://pypi.python.org/pypi/{}/json'.format(split_name)
                pypi_json = requests.get(url)
                data = pypi_json.json()
                upstream_version = data['info']['version'][:]
                project_url = data['info']['project_url'][:]
                download_url = data['urls']
                for item in download_url:
                    if item['python_version'] == 'source':
                         archive = item['url']
               # print(json.dumps(download_url))
                return upstream_version, project_url, archive

            pypi_json = requests.get(url)
            data = pypi_json.json()
            upstream_version = data['info']['version'][:]
            project_url = data['info']['project_url'][:]
            download_url = data['urls']
            for item in download_url:
                if item['python_version'] == 'source':
                     archive = item['url']
            #print(json.dumps(download_url))
            return upstream_version, project_url, archive

        if req.status_code == 200:
            pypi_json = requests.get(url)
            data = pypi_json.json()
            #print(data)
            upstream_version = data['info']['version'][:]
            project_url = data['info']['project_url'][:]
            download_url = data['urls']
            print(download_url)
            for item in download_url:
                 if item['python_version'] == 'source':
                     archive = item['url']
            #print(json.dumps(download_url))
            return upstream_version, project_url, archive
    except:
        pass

def any_other(upstream_url, package):
    split_url = upstream_url.split("/")[:6]
    project_url = '/'.join(split_url[:5])
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




def check_version(package):
    print('checking upstream version for package [{}]'.format(package))
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
            get_nvs(spec_path)
            name = nvs[0]
            version = nvs[1]
            source = nvs[2]
            source0 = nvs[3]
            #print(name, version, source, source0)
            nvss.extend([name, version, source, source0])
            return name, version, source, source0
        except:
            pass
        finally:
            temp.close()


def tryint(x):
    try:
        return int(x)
    except ValueError:
        return x


def splittedname(s):
    return tuple(tryint(x) for x in re.split('([0-9]+)', s))


def check_upstream(package):
    upstream_name, our_ver, upstream_url, source0 = nvss
    if 'github' in upstream_url:
        upstream_version, upstream_url = github_check(upstream_url)
        print('upstream version is [{}]'.format(upstream_version))
        print('upstream url is [{}]'.format(upstream_url))
        print('=========================================')
        return upstream_version, upstream_url
    elif 'pypi' or 'python' in upstream_url:
        upstream_version, upstream_url, archive = check_python_module(package)
        print('upstream version is [{}]'.format(upstream_version))
        print('upstream archive is [{}]'.format(archive))
        print('=========================================')
        return upstream_version, upstream_url, archive
    else:
        return any_other(upstream_url, package)


def compare_versions(package):
    try:
        name, omv_version, url, source0 = nvss
        print(name, omv_version, url, source0)
        print('check upstream')
        upstream_ver, upstream_url, *archive = check_upstream(package)
        if len(archive) == 1:
            archive = archive[0]
        else:
            archive = None
        package_item = {
            'package': package,
            'omv_version': omv_version,
            'upstream_version': upstream_ver,
            'project_url': upstream_url
        }
        print(package_item)
        if archive is not None:
            package_item['archive'] = archive
        if splittedname(omv_version) == splittedname(upstream_ver):
            package_item['status'] = 'updated'
        if splittedname(omv_version) < splittedname(upstream_ver):
            package_item['status'] = 'outdated'
        if splittedname(omv_version) > splittedname(upstream_ver):
            package_item['status'] = 'unknown'
        return package_item
    except:
        pass


def remove_if_exist(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            try:
                subprocess.check_output(
                    ['/usr/bin/sudo', '-E', 'rm', '-rf', path])
            except subprocess.CalledProcessError as e:
                print(e.output)
                return
        if os.path.isfile(path):
            try:
                subprocess.check_output(
                    ['/usr/bin/sudo', '-E', 'rm', '-f', path])
            except subprocess.CalledProcessError as e:
                print(e.output)
                return

def clone_repo(package, project_version):
    remove_if_exist(home + '/' + package)
    tries = 5
    git_repo = 'git@github.com:OpenMandrivaAssociation/{}.git'.format(package)
    for i in range(tries):
        try:
          print('cloning [{}], branch: [{}] to [{}]'.format(git_repo, project_version, package))
          subprocess.check_output(['/usr/bin/git', 'clone', '-b', project_version, '--depth', '100', git_repo, package], cwd = home)
        except subprocess.CalledProcessError:
            if i < tries - 1:
                time.sleep(5)
                continue
            else:
                print('some issues with cloning repo %s' % git_repo)
                sys.exit(1)
        break

def remove_if_exist(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            try:
                subprocess.check_output(
                    ['rm', '-rf', path])
            except subprocess.CalledProcessError as e:
                print(e.output)
                return
        if os.path.isfile(path):
            try:
                subprocess.check_output(
                    ['rm', '-f', path])
            except subprocess.CalledProcessError as e:
                print(e.output)
                return

def lint_version(version):
    return re.search('[a-zA-Z]', version) is not None

def git_commit(message, package):
    try:
        subprocess.check_call(['git', 'commit', '-am', '{}'.format(message)], cwd = home + '/' + package)
    except subprocess.CalledProcessError as e:
        sys.exit(1)
        print(e)


def git_push(package):
    try:
        subprocess.check_call(['git', 'push'], cwd = home + '/' + package)
    except subprocess.CalledProcessError as e:
        sys.exit(1)
        print(e)


def upload_sources(package):
    abf_yml = home + '/' + package + '/' + '.abf.yml'
    remove_if_exist(abf_yml)
    try:
        subprocess.check_call(['abf', 'put'], cwd = home + '/' + package)
    except subprocess.CalledProcessError as e:
        print_log('uploading sources [{}] failed'.format(package), 'update.log')
        print(e)


def abf_build(package):
    try:
        subprocess.check_call(['abf', 'chain_build', '-b', 'master', '--no-cached-chroot', '--auto-publish', '--update-type', 'enhancement', 'openmandriva/{}'.format(package)], cwd = home + '/' + package)
    except subprocess.CalledProcessError as e:
        print_log('abf build [{}] failed'.format(package), 'update.log')
        print(e)
        return False


def update_spec(package):
    pkg_status = compare_versions(package)
    status = pkg_status['status']
    upstream_version = pkg_status['upstream_version']
    omv_version = pkg_status['omv_version']
    if 'archive' in pkg_status:
        new_source0 = pkg_status['archive']
        print(new_source0)
    else:
        new_source0 = None
    output = '/tmp/' + package + '.spec'
    remove_if_exist(output)
    print('linting version')
    try:
       if lint_version(upstream_version) is False and status == 'outdated':
           print('update required')
           # find current version
           clone_repo(package, project_version)
           version_pattern = 'Version:\W*({})'.format(omv_version)
           specname = home + '/' + package + '/' + package + '.spec'
           with open(specname) as f:
               for line in f:
                   change_version = re.sub(version_pattern, 'Version:\t' + upstream_version, line)
                   with open(output, 'a') as outfile:
                       outfile.write(change_version)
               target_spec = home + '/' + package + '/' + package + '.spec'
               shutil.move(output, target_spec)
           if new_source0 is not None:
               source_pattern = 'Source0:\W*(.*)'
               with open(specname) as f:
                   for line in f:
                       change_source = re.sub(source_pattern, 'Source0:\t' + new_source0, line)
                       with open(output, 'a') as outfile:
                           outfile.write(change_source)
                   target_spec = home + '/' + package + '/' + package + '.spec'
                   shutil.move(output, target_spec)
           if run_local_builder(package, project_version) is not False:
               upload_sources(package)
               git_commit('version autoupdate [{}]'.format(upstream_version), package)
               git_push(package)
               abf_build(package)
    except:
        pass

def print_log(message, log):
    try:
        logFile = open(log, 'a')
        logFile.write(message + '\n')
        logFile.close()
    except:
        print("Can't write to log file: " + log)
    print(message)


def run_local_builder(package, project_version):
    try:
        print('run local build with abf tool')
        subprocess.check_call(['spectool', '--get-files', package + '.spec'], cwd = home + '/' + package)
        subprocess.check_call(['abf', 'mock'], cwd = home + '/' + package)
    except subprocess.CalledProcessError as e:
        print_log('local build [{}] failed'.format(package), 'update.log')
        print(e)
        sys.exit(1)

#update_spec('vim')
if __name__ == '__main__':
    weird_list = []
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', nargs='+', help='package to upgrade')
    parser.add_argument('--file', help='file with packages list')
    args = parser.parse_args()
    if args.file is not None:
        with open(args.file) as file:
             for line in file:

                 # clear lists
                 del nvss[:]
                 del nvs[:]
                 print(line.strip())
                 package = line.strip()
                 check_version(package)
                 try:
                     update_spec(package)
                 except:
                     pass
                
    if args.package is not None:
        packages = [i for i in args.package if i is not None]
        for package in packages:
            # clear lists
            del nvss[:]
            del nvs[:]
            check_version(package)
            try:
                update_spec(package)
            except:
                pass

#update_spec('python-sqlalchemy')
#check_upstream('vim')
#compare_versions('python-sqlalchemy')
#compare_versions('python-coverage')
#compare_versions('vim')
#compare_versions('sway')

