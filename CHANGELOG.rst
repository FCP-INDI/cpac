=========
Changelog
=========

`Version 1.8.6: Support for C-PAC v1.8.6 <https://github.com/FCP-INDI/cpac/releases/tag/v1.8.6>`_
=====================================================================================================

* Fixes a bug in checking for C-PAC version

`Version 1.8.5: Support for C-PAC v1.8.5 <https://github.com/FCP-INDI/cpac/releases/tag/v1.8.5>`_
=====================================================================================================

* Changes versioning scheme to match supported C-PAC version
* Handles relocation of default pipeline in C-PAC 1.8.5
* Fixes a bug preventing default bindings in Mac OS ≥ 10.15
* Replaces ``setup.cfg`` with ``pyproject.toml``
* Replaces ``setuptools`` with ``poetry``
* Adds pre-commit hooks for linting and formatting
* Require Python ≥ 3.8

`Version 0.5.0: Parse Resources <https://github.com/FCP-INDI/cpac/releases/tag/v0.5.0>`_
========================================================================================
* 🧮 Evaluates memory usage for specific nodes from ``callback.log`` files
* ✨ Adds ``enter`` command to enter a container's ``BASH``
* ✨ Adds ``version`` command to give version of in-container C-PAC
* ✨ Adds ``parse-resources`` command to parse resources from ``callback.log``
* 🐛 Fixes issue where ``--version`` command was not working
* 🐛 Fixes issue where custom pipeline configurations were not binding to temporary container prior to checking for bind paths
* ✅ Updates for tests that were failing
* 📝 Add known issues to usage string
* ⬆ Require Python ≥ 3.7 (for typing annotations)
* 📝 Documents support for Singularity 3

`Version 0.4.0: Goodbye Singularity Hub <https://github.com/FCP-INDI/cpac/releases/tag/v0.4.0>`_
================================================================================================
* 👽 Drop call to now-deprecated Singularity Hub
* 🐛 Resolves issue where minimal configs would cause wrapper to crash

`Version 0.3.2: Pull / Upgrade <https://github.com/FCP-INDI/cpac/releases/tag/v0.3.2>`_
========================================================================================
* ➖ Remove dependecy on Nipype
* 🐛 Pass commandline arguments through to ``cpac crash``
* 🚸 Add ``pull`` / ``upgrade`` command
* ⚡️🐳 Stop Docker containers when finished
* 👽 Handle changes from C-PAC 1.7 to 1.8
* 👷 Move tests from Travis to GitHub Actions
* 📝 Note needlessness of crash command for C-PAC ≥ 1.8.0
* 🚸 Use repeated flags in place of multi-value tags

`Version 0.3.1 <https://github.com/FCP-INDI/cpac/releases/tag/v0.3.1>`_
=======================================================================
* 🚸 Print without emoji if terminal can't handle extended Unicode set
* 📚 Add PyPI badge to README

`Version 0.3.0 <https://github.com/FCP-INDI/cpac/releases/tag/v0.3.0>`_
=======================================================================
* 📛 Rename project from `shnizzedy/cpac-python-package <https://github.com/shnizzedy/cpac-python-package>`_ to `FCP-INDI/cpac <https://github.com/FCP-INDI/cpac>`_
* 📦 Reclassify from `pre-alpha <https://en.wikipedia.org/wiki/Software_release_life_cycle#Pre-alpha>`_ to `alpha <https://en.wikipedia.org/wiki/Software_release_life_cycle#Alpha>`_

`Version 0.2.5 <https://github.com/shnizzedy/cpac/releases/tag/v0.2.5>`_
========================================================================
* 📚 Update the main usage string to better articulate functionality
* 📢🐳 Provide a clearer error message if package cannot connect to Docker.
* 🐳 Fix a bug introduced in `v0.2.4 <https://github.com/shnizzedy/cpac/releases/tag/v0.2.4>` where some crashfiles would print for ``cpac --platform singularity crash`` but not for ``cpac --platform docker crash``
* 🚑 Fix some installation issues:
   * All required packages are now installed with ``pip install cpac``
   * Version is now set correctly
* 🐳 Fix a bug introduced in `v0.2.4 <https://github.com/shnizzedy/cpac/releases/tag/v0.2.4>`_ where some crashfiles would print for ``cpac --platform singularity crash`` but not for ``cpac --platform docker crash``
* 🔬 Set `coverage reports <http://coveralls.io/github/shnizzedy/cpac>`_ to report local paths

`Version 0.2.4 <https://github.com/shnizzedy/cpac/releases/tag/v0.2.4>`_
========================================================================
* 💪 Make ``crash`` command automatically touch (within a container) all missing files a crashfile requires to exist and print the underlying output
* 🐳 Make Docker commands (especially ``pull`` and ``crash``) more robust
* ⬆️ Require Python ≥3.6 (for fstrings)

`Version 0.2.3: Crashfile <https://github.com/shnizzedy/cpac/releases/tag/v0.2.3>`_
========================================================================================
* ✨ Added ``group`` and ``crash`` commands
* 🚑 Fixed a bug where pass-through flags were being mangled
* 🖇️ Binds any directories necessary to access any paths found in pass-through CLI arguments

`Version 0.2.2: Autobind <https://github.com/shnizzedy/cpac/releases/tag/v0.2.2>`_
========================================================================================

Version 0.2.2.post1
-------------------
* 🖉 Pass ``run -h`` through like ``run --help``

Version 0.2.2
-------------
* ✨ Automatic binding of necessary local directories to Docker or Singularity
* 📚 Pass ``run --help`` through to container without positional arguments to get full current helpstring

Version 0.2.1
=============
* Ⓢ Enabled specifying Singularity image file or Docker tag for Singularity

Version 0.2.0
=============
* ✨Ⓢ Added Singularity support

Version 0.1.5
=============
* ⬆ Added installation depenencies

Version 0.1.4
=============
* 🚑 Removed erroneous import statement

Version 0.1.3
=============
* ➕ Require ``docker-pycreds``, ``websocket-client``

Version 0.1.2
=============
* 🚑 Fixed bug preventing binding the same local directory to multiple Docker directories

Version 0.1.1
=============

* ✨ Added support for ``pip install``
* ✨ Added support for ``cpac run``
* ✨ Added support for ``cpac utils``
* 🔊🐳 Routed live Docker logging to stdout
* 🔬 Added tests for ``cpac run`` and ``cpac utils``

Version 0.1.0
=============
* ✨🐳 Ported Docker support from Theodore
