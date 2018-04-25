.. Incident Store documentation master file, created by
   sphinx-quickstart on Tue Apr 17 11:19:57 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Incident Store's documentation!
==========================================

`bos-incidents` stores incidents from the data-proxies in a mongodb so
it's status can be tracked and displayed via command line tools in
`bos-auto` or the web interface `bos-mint`.

Default implementation requires a mongodb server running locally
(`localhost:27017`).

.. code-block:: python

     from bos_incidents import factory
     storage = factory.get_incident_storage()
     incidents = storage.get_incidents_by_id({
             "home": "Charlotte Hornets",
             "start_time": "2018-03-22T23:00:00Z",
             "event_group_name": "NBA Regular Season",
             "away": "Memphis Grizzlies",
             "sport": "Basketball"
         }
     )

Installation
------------

.. code-block:: shell

    $ pip3 install bos-incidents

API
---
.. toctree::
   :maxdepth: 3
   :caption: Contents:

   bos_incidents
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
