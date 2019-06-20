#!/usr/bin/env python
import subprocess
import os
import sys
import time
import requests
import json
import re
import shutil
import argparse

home = os.environ.get('HOME')
package_status = 'https://gist.github.com/fedya/a300af51a5eba8b00aad2421ecc3bdc3/raw/d51eb92562ae49b6fd3fe0d9d3121b112b7f9b11/gistfile1.txt'
project_version = 'master'

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

def get_json_data(package):
    current_status = ''
    upstream_ver = ''
    omv_ver = ''
    response = requests.get(package_status)
    json_data = json.loads(response.text)
    try:
        for i in json_data['packages']:
            if i['package'] == package:
                current_status = i['status']
                upstream_ver = i['upstream_version']
                omv_ver = i['omv_version']
                print('current status: [{}], upstream version: [{}], omv version: [{}]'.format(current_status, upstream_ver, omv_ver))
                return current_status, upstream_ver, omv_ver
    except ValueError:
        return current_status, upstream_ver, omv_ver

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
    output = '/tmp/' + package + '.spec'
    remove_if_exist(output)
    try:
        current_status, upstream_ver, omv_ver = get_json_data(package)
        print('linting version')
        print(current_status)
        if lint_version(upstream_ver) is False and current_status == 'outdated':
            print('update required')
            # find current version
            clone_repo(package, project_version)
            pattern = 'Version:\W*({})'.format(omv_ver)
            specname = home + '/' + package + '/' + package + '.spec'
            with open(specname) as f:
                for line in f:
                    change_version = re.sub(omv_ver, upstream_ver, line)
                    with open(output, 'a') as outfile:
                        outfile.write(change_version)
                target_spec = home + '/' + package + '/' + package + '.spec'
                shutil.move(output, target_spec)
            if run_local_builder(package, project_version) is not False:
                upload_sources(package)
                git_commit('version autoupdate [{}]'.format(upstream_ver), package)
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
        subprocess.check_call(['pwd'], cwd = home + '/' + package)
        #subprocess.check_call(['spectool', '--define', '_disable_source_fetch 1', '--get-files', '*.spec'], cwd = home + '/' + package)
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
            try:
                for line in file:
                    update_spec(line.strip())
            except:
                print('shit happened')
    if args.package is not None:
        packages = [i for i in args.package if i is not None]
        for package in packages:
            update_spec(package)

