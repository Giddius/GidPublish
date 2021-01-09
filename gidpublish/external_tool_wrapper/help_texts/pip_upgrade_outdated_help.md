# PIP_UPGRADE_OUTDATED

```console
usage: pip_upgrade_outdated [-h] [-3 | -2 | --pip_cmd PIP_CMD]
                            [--serial | --parallel | --sequential] [--user]
                            [--dry_run] [--verbose] [--version]
                            [--exclude PKG]

Upgrade outdated python packages with pip. Any unknown arguments will be
passed to pip.

optional arguments:
  -h, --help            show this help message and exit
  -3                    use pip3
  -2                    use pip2
  --pip_cmd PIP_CMD     use PIP_CMD (default pip)
  --serial, -s          upgrade in serial via a single batch pip upgrade
                        command (default)
  --parallel, -p        upgrade in parallel via individual pip ugrade commands
  --sequential, -q      upgrade in serial via individual pip ugrade commands
  --user, -u            Adds the --user flag when installing the packages
  --dry_run, -n         get list, but don't upgrade
  --verbose, -v         may be specified multiple times
  --version             show program's version number and exit
  --exclude PKG, -x PKG
                        exclude PKG; may be specified multiple times

```