import os
import subprocess

this_dir = os.path.dirname(__file__)

image = None

def build_image():
    global image
    if image is None:
        owd = os.getcwd()
        try:
            os.chdir(this_dir)
            proc_command = [
                'singularity',
                'build',
                '--fakeroot',
                '--force',
                '/tmp/cpacpy-singularity_test.sif',
                os.path.join(this_dir, 'Singularity'),
            ]
            process = subprocess.Popen(proc_command)
            process.wait()

            image = '/tmp/cpacpy-singularity_test.sif'
        finally:
            os.chdir(owd)
            
    return image