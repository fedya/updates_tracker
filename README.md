# OpenMandriva Autoupdater

A tool to autoupdate packages

## Installation

Generate [GitHub API token](https://github.com/settings/tokens).

```bash
git clone git@github.com:fedya/updates_tracker.git
sudo dnf install abf-c-c mock rpmdevtools
sudo gpasswd -a $USER mock
```

Than edit [new_checker.py](https://github.com/fedya/updates_tracker/blob/master/new_checker.py#L16)
you need to replace github_token with obtained one.

## Usage
Check [sway](https://github.com/swaywm/sway) version
```bash
python new_checker.py --package sway
[....]
{
	'package': 'sway',
	'omv_version': '1.1.1',
	'upstream_version': '1.1.1',
	'project_url': 'https://github.com/SirCmpwn/sway/'
}
```
or check [vim](https://github.com/vim)
```bash
python new_checker.py --package vim
[....]
{
	'package': 'vim',
	'omv_version': '8.1.1592',
	'upstream_version': '8.1.1592',
	'project_url': 'https://github.com/vim/vim/'
}
```

## How it Works
1. Asks OpenMandriva repo https://github.com/OpenMandrivaAssociation/ for current version
2. Detect upstream url and make request to github/repology api to pull new version
3. Run local build with abf-c-c tool
4. if succeeded run git commit with version ```autoupdate [1.1.27]``` message
5. Git push and run abf build

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
