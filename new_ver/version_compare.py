def tryint(x):
    try:
        return int(x)
    except ValueError:
        return x

def splittedname(s):
    return tuple(tryint(x) for x in re.split('([0-9]+)', s))

def compare_versions(package):
    our_ver = check_version(package)
    upstream_ver, project_url = check_upstream(package)
    a = splittedname(our_ver)
    b = splittedname(upstream_ver)

    package_item = {
        'package': package,
        'omv_version': our_ver,
        'upstream_version': upstream_ver,
        'project_url': project_url
    }
    if splittedname(our_ver) == splittedname(upstream_ver):
        package_item['status'] = 'no updates required'
    if splittedname(our_ver) < splittedname(upstream_ver):
        package_item['status'] = 'outdated'
    if splittedname(our_ver) > splittedname(upstream_ver):
        package_item['status'] = 'omv version is newer'

    return package_item
