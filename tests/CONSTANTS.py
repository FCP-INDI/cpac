import os

from cpac.utils import ls_newest


def SINGULARITY_OPTION():
    singularity_option = ls_newest(os.getcwd(), ['sif', 'simg'])
    return(f'--image {singularity_option}' if (
        singularity_option is not None
    ) else '--platform singularity')
