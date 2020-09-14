===============
Welcome to MIST
===============


Asynchronous HTTP Client/Server for :term:`asyncio` and Python.

.. _GitHub: https://github.com/cr0hn/mist


Key Features
============

- Supports both :ref:`aiohttp-client` and :ref:`HTTP Server <aiohttp-web>`.
- Supports both :ref:`Server WebSockets <aiohttp-web-websockets>` and
  :ref:`Client WebSockets <aiohttp-client-websockets>` out-of-the-box
  without the Callback Hell.
- Web-server has :ref:`aiohttp-web-middlewares`,
  :ref:`aiohttp-web-signals` and plugable routing.

.. _aiohttp-installation:

Library Installation
====================

.. code-block:: bash

   $ pip install mist

Getting Started
===============


.. code-block:: text

   asdf

Tutorial
========

:ref:`Polls tutorial <aiohttp-demos-polls-beginning>`


Source code
===========

The project is hosted on GitHub_

Please feel free to file an issue on the `bug tracker
<https://github.com/cr0hn/mist/issues>`_ if you have found a bug
or have some suggestion in order to improve the library.

Contributing
============

Please read the :ref:`instructions for contributors<aiohttp-contributing>`
before making a Pull Request.


License
=======

It's *BSD 3* licensed and freely available.


Table Of Contents
=================

.. toctree::
   :name: mastertoc
   :maxdepth: 2

   client
   web
   utilities
   faq
   misc
   external
   contributing
