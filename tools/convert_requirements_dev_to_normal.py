# * Standard Library Imports -->
import os

THIS_FILE_DIR = os.path.abspath(os.path.dirname(__file__))
REQU_DEV_FILE = "../requirements_dev.txt"
REQU_NORM_FILE = "../requirements.txt"

old_cwd = os.getcwd()


def convert():
    os.chdir(THIS_FILE_DIR)
    with open(REQU_DEV_FILE, 'r') as devreq:
        dev_lines = devreq.read().splitlines()
    with open(REQU_NORM_FILE, 'w') as req:
        for line in dev_lines:
            if line != '' and 'git+' not in line:
                req.write(line + '\n')
    os.chdir(old_cwd)


if __name__ == '__main__':
    convert()
