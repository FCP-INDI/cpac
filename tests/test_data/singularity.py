import os
from spython.main import Client

this_dir = os.path.dirname(__file__)

def build_image():
    owd = os.getcwd()
    try:
        os.chdir(this_dir)
        out = Client.build(
            build_folder=this_dir,
            image='/tmp/cpacpy-test.sif',
            recipe=os.path.join(this_dir, 'Singularity'),
            sudo=False,
            force=True,
            options=['--fakeroot'],
        )
    finally:
        os.chdir(owd)
    return '/tmp/cpacpy-test.sif'