=========
Changelog
=========

`Version 0.2.2: Autobind <https://github.com/shnizzedy/cpac-python-package/releases/tag/v0.2.2>`_
=================================================================================================

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
