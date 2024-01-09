====================
C-PAC Python Package
====================

|build-status| |github-version| |upload| |pypi-version| |coverage|

A Python package that wraps `C-PAC <http://fcp-indi.github.io>`_, enabling users to install cpac with `pip <https://pip.pypa.io>`_ and run from the command line.


Description
===========

cpac Python Package is a lightweight Python package that handles interfacing a user's machine and a C-PAC container through a command line interface.

.. admonition:: Note about cpac versioning

    This package's versioning scheme changed in version 1.8.5 to match C-PAC's versioning. From cpac v1.8.5 forward, the version of cpac indicates the newest supported version of C-PAC.

Dependencies
============

* `Python <https://www.python.org>`_ ≥ 3.8
* `pip <https://pip.pypa.io>`_
* At least one of:

  * `Docker <https://www.docker.com>`_
  * `Singularity <https://sylabs.io/singularity>`_ ≥2.5

Usage
=====

.. BEGIN USAGE

.. code-block:: shell

    cpac --help
    usage: cpac [-h] [--version] [-o OPT] [-B CUSTOM_BINDING]
                [--platform {docker,singularity}] [--image IMAGE] [--tag TAG]
                [--working_dir PATH] [-v] [-vv]
                {run,utils,version,group,pull,upgrade,enter,bash,shell,parse-resources,parse_resources,crash}
                ...
    
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
    
    Known issues:
    - Some Docker containers unexpectedly persist after cpac finishes. To clear them, run
        1. `docker ps` to list the containers
      For each C-PAC conatainer that persists, run
        2. `docker attach <container_name>`
        3. `exit`
    - https://github.com/FCP-INDI/cpac/issues
    
    positional arguments:
      {run,utils,version,group,pull,upgrade,enter,bash,shell,parse-resources,parse_resources,crash}
        run                 Run C-PAC. See
                            "cpac [--platform {docker,singularity}] [--image IMAGE] [--tag TAG] run --help"
                            for more information.
        utils               Run C-PAC commandline utilities. See
                            "cpac [--platform {docker,singularity}] [--image IMAGE] [--tag TAG] utils --help"
                            for more information.
        version             Print the version of C-PAC that cpac is using.
        group               Run a group level analysis in C-PAC. See
                            "cpac [--platform {docker,singularity}] [--image IMAGE] [--tag TAG] group --help"
                            for more information.
        pull (upgrade)      Upgrade your local C-PAC version to the latest version
                            by pulling from Docker Hub or other repository.
                            Use with "--image" and/or "--tag" to specify an image
                            other than the default "fcpindi/c-pac:latest" to pull.
        enter (bash, shell)
                            Enter a new C-PAC container via BASH.
        parse-resources (parse_resources)
                            .
                            
                            When provided with a `callback.log` file, this utility can sort through
                            the memory `runtime` usage, `estimate`, and associated `efficiency`, to
                            identify the `n` tasks with the `highest` or `lowest` of each of these
                            categories.
                            "parse-resources" is intended to be run outside a C-PAC container.
                            See "cpac parse-resources --help" for more information.
        crash               Convert a crash pickle to plain text (C-PAC < 1.8.0).
    
    options:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -o OPT, --container_option OPT
                            parameters and flags to pass through to Docker or Singularity
                            
                            This flag can take multiple arguments so cannot be
                            the final argument before the command argument (i.e.,
                            run or any other command that does not start with - or --)
      -B CUSTOM_BINDING, --custom_binding CUSTOM_BINDING
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
