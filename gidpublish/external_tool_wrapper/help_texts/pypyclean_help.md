# PYPYCLEAN

```console
usage: pypyclean [-h] [--version] [-V VERSION] [-p PACKAGE] [--legacy] [-n]
                 [-q | -v]
                 [directory ...]

Remove byte-compiled files for a package

positional arguments:
  directory             Directory tree (or file) to byte-compile

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -V VERSION            specify Python version to clean
  -p PACKAGE, --package PACKAGE
                        Debian package to byte-compile (may be specified
                        multiple times)
  --legacy              Use legacy Debian implementation (autodetect)
  -n, --dry-run         Show what would be done
  -q, --quiet           Be quiet
  -v, --verbose         Be more verbose

```