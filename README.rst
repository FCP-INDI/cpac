===============================================================
C-PAC Python Package |github-version| |build-status| |coverage|
===============================================================

A Python package that wraps `C-PAC <http://fcp-indi.github.io>`_, enabling users to install cpac with `pip <https://pip.pypa.io>`_ and run from the command line.


Description
===========

C-PAC Python Package is a lightweight Python package that handles interfacing a user's machine and a C-PAC container through a command line interface.

Dependencies
============

* `Python <https://www.python.org>`_ ≥3.5
* `pip <https://pip.pypa.io>`_
* At least one of:

    * `Docker <https://www.docker.com>`_
    * `Singularity <https://sylabs.io/singularity>`_ ≥2.5&≤3.0

Usage
=====

.. BEGIN USAGE

.. code-block:: shell

    cpac --help
    usage: cpac [-h] [--platform {docker,singularity}] [--image IMAGE] [--tag TAG]
                [--version] [-v] [-vv] [--working_dir PATH] [--temp_dir PATH]
                [--output_dir PATH] [-o OPT [OPT ...]]
                {run,utils} ...
    
    cpac: a Python package that simplifies using C-PAC <http://fcp-indi.github.io>
    containerized images. If no platform nor image is specified, cpac will try
    Docker first, then try Singularity if Docker fails.
    
    positional arguments:
      {run,utils}
    
    optional arguments:
      -h, --help            show this help message and exit
      --platform {docker,singularity}
      --image IMAGE         path to Singularity image file OR name of Docker image
                            (eg, "fcpindi/c-pac"). Will attempt to pull from
                            Singularity Hub or Docker Hub if not provided.
      --tag TAG             tag of the Docker image to use (eg, "latest" or
                            "nightly").
      --version             show program's version number and exit
      -v, --verbose         set loglevel to INFO
      -vv, --very-verbose   set loglevel to DEBUG
      --working_dir PATH    working directory
      --temp_dir PATH       directory for temporary files
      --output_dir PATH     directory where output files should be stored
      -o OPT [OPT ...], --container_options OPT [OPT ...]
                            parameters and flags to pass through to Docker or
                            Singularity

.. END USAGE

.. |github-version| image:: https://img.shields.io/github/tag/shnizzedy/cpac-python-package.svg
    :target: https://github.com/shnizzedy/cpac-python-package/releases
    :alt: GitHub version
.. |build-status| image:: https://travis-ci.org/shnizzedy/cpac-python-package.svg?branch=master
    :target: https://travis-ci.org/shnizzedy/cpac-python-package
    :alt: Travis CI build status
.. |coverage| image:: https://coveralls.io/repos/github/shnizzedy/cpac-python-package/badge.svg?branch=master
    :target: https://coveralls.io/github/shnizzedy/cpac-python-package?branch=master
    :alt: coverage badge
