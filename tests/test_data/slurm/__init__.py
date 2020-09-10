import os
import subprocess

this_dir = os.path.dirname(__file__)


def spinup_cluster():
    owd = os.getcwd()
    try:
        os.chdir(this_dir)
        subprocess.Popen(['docker-compose', 'up', '-d'])
        subprocess.Popen(['bash', './register_cluster.sh']).wait()
    finally:
        os.chdir(owd)


def spindown_cluster():
    owd = os.getcwd()
    try:
        os.chdir(this_dir)
        subprocess.Popen(['docker-compose', 'down', '-v']).wait()
    finally:
        os.chdir(owd)