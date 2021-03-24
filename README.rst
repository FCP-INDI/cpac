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

