import os
import subprocess

this_dir = os.path.dirname(__file__)

image = {}

def build_image(fakeroot=True, type='sif'):
    global image
    if not image.get((fakeroot, type)):
        owd = os.getcwd()
        try:
            image_path = f'/tmp/cpacpy-singularity_test{"_fakeroot" if fakeroot else ""}.{type}'
            os.chdir(this_dir)
            proc_command = filter(None, [
                'singularity',
                'build',
                '--fakeroot' if fakeroot else None,
                '--force',
                image_path,
                os.path.join(this_dir, 'Singularity'),
            ])
            process = subprocess.Popen(proc_command)
            process.wait()
        finally:
            os.chdir(owd)

        image[(fakeroot, type)] = image_path

    return image.get((fakeroot, type))