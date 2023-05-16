Introduction
============


.. image:: https://readthedocs.org/projects/adafruit-circuitpython-json-stream/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/json_stream/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_JSON_Stream/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_JSON_Stream/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black


This library is a reimplementation and subset of `json_stream <https://github.com/daggaz/json-stream>`_. It enables reading JSON data from a stream rather that loading it all into memory at once. The interface works like lists and dictionaries that are usually returned from ``json.load()`` but require in-order access. Out of order accesses will lead to missing keys and list entries.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================

This library is on PyPI for editors that use it for CircuitPython. In CPython,
it is recommended to use `json_stream <https://github.com/daggaz/json-stream>`_ itself.

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_json_stream

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import ssl
    import time
    import adafruit_requests
    import socketpool
    import wifi
    import adafruit_json_stream as json_stream

    pool = socketpool.SocketPool(wifi.radio)
    session = adafruit_requests.Session(pool, ssl.create_default_context())

    SCORE_URL = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"

    while True:
        resp = session.get(SCORE_URL)
        json_data = json_stream.load(resp.iter_content(32))
        for event in json_data["events"]:
            if "Seattle" not in event["name"]:
                continue
            for competition in event["competitions"]:
                for competitor in competition["competitors"]:
                    print(competitor["team"]["displayName"], competitor["score"])
        resp.close()
        time.sleep(60)

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/json_stream/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_JSON_Stream/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
