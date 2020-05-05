import os

from cpac.utils import ls_newest


SINGULARITY_OPTION = ls_newest(os.getcwd(), 'simg')
SINGULARITY_OPTION = f'--image {SINGULARITY_OPTION}' if (
    SINGULARITY_OPTION is not None
) else '--platform singularity'