========================================================================================
C-PAC Python Package |build-status| |github-version| |upload| |pypi-version| |coverage|
========================================================================================


A Python package that wraps `C-PAC <http://fcp-indi.github.io>`_, enabling users to install cpac with `pip <https://pip.pypa.io>`_ and run from the command line.


Description
===========

C-PAC Python Package is a lightweight Python package that handles interfacing a user's machine and a C-PAC container through a command line interface.

Dependencies
============

* `Python <https://www.python.org>`_ ≥3.6
* `pip <https://pip.pypa.io>`_
* At least one of:

  * `Docker <https://www.docker.com>`_
  * `Singularity <https://sylabs.io/singularity>`_ ≥2.5&≤3.0

Usage
=====

.. BEGIN USAGE

.. code-block:: shell

    cpac --help
    usage: cpac [-h] [--version] [-o [OPT [OPT ...]]]
                [-B [CUSTOM_BINDING [CUSTOM_BINDING ...]]]
                [--platform {docker,singularity}] [--image IMAGE] [--tag TAG]
                [--working_dir PATH] [-v] [-vv]
                {run,group,utils,pull,upgrade,crash} ...
    
    cpac: a Python package that simplifies using C-PAC <http://fcp-indi.github.io> containerized images. 
    
    This commandline interface package is designed to minimize repetition.
    As such, nearly all arguments are optional.
    
    When launching a container, this package will try to bind any paths mentioned in 
     • the command
     • the data configuration
    
    An example minimal run command:
    	cpac run /path/to/data /path/for/outputs
    
    An example run command with optional arguments:
    	cpac -B /path/to/data/configs:/configs \
    		--image fcpindi/c-pac --tag latest \
    		run /path/to/data /path/for/outputs \
    		--data_config_file /configs/data_config.yml \
    		--save_working_dir
    
    Each command can take "--help" to provide additonal usage information, e.g.,
    
    	cpac run --help
    
    positional arguments:
      {run,group,utils,pull,upgrade,crash}
    
    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -o [OPT [OPT ...]], --container_option [OPT [OPT ...]]
                            parameters and flags to pass through to Docker or Singularity
                            
                            This flag can take multiple arguments so cannot be
                            the final argument before the command argument (i.e.,
                            run or any other command that does not start with - or --)
      -B [CUSTOM_BINDING [CUSTOM_BINDING ...]], --custom_binding [CUSTOM_BINDING [CUSTOM_BINDING ...]]
                            directories to bind with a different path in
                            the container than the real path of the directory.
                            One or more pairs in the format:
                            	real_path:container_path
                            (eg, /home/C-PAC/run5/outputs:/outputs).
                            Use absolute paths for both paths.
                            
                            This flag can take multiple arguments so cannot be
                            the final argument before the command argument (i.e.,
                            run or any other command that does not start with - or --)
      --platform {docker,singularity}
                            If neither platform nor image is specified,
                            cpac will try Docker first, then try
                            Singularity if Docker fails.
      --image IMAGE         path to Singularity image file OR name of Docker image (eg, "fcpindi/c-pac").
                            Will attempt to pull from Singularity Hub or Docker Hub if not provided.
                            If image is specified but platform is not, platform is
                            assumed to be Singularity if image is a path or 
                            Docker if image is an image name.
      --tag TAG             tag of the Docker image to use (eg, "latest" or "nightly").
      --working_dir PATH    working directory
      -v, --verbose         set loglevel to INFO
      -vv, --very-verbose   set loglevel to DEBUG

.. END USAGE

.. |pypi-version| image:: https://badge.fury.io/py/cpac.svg
    :target: https://pypi.org/project/cpac/
    :alt: PyPI version
.. |github-version| image:: https://img.shields.io/github/tag/FCP-INDI/cpac.svg
    :target: https://github.com/FCP-INDI/cpac/releases
    :alt: GitHub version
.. |build-status| image:: https://github.com/FCP-INDI/cpac/actions/workflows/test_cpac.yml/badge.svg
    :target: https://github.com/FCP-INDI/cpac/actions/workflows/test_cpac.yml
    :alt: GitHub Action: Test cpac
.. |coverage| image:: https://coveralls.io/repos/github/FCP-INDI/cpac/badge.svg
    :target: https://coveralls.io/github/FCP-INDI/cpac
    :alt: coverage badge
.. |upload| image:: https://github.com/FCP-INDI/cpac/workflows/Upload%20Python%20Package/badge.svg
    :target: https://pypi.org/project/cpac/
    :alt: upload Python package to PyPI

