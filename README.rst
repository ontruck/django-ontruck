=============================
django-ontruck
=============================



|build-status| |coverage| |license|



Django extended by Ontruck-ers

Documentation
-------------

The full documentation is at https://django-ontruck.readthedocs.io.

Quickstart
----------

Install django-ontruck::

    pip install django-ontruck

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_ontruck',
        ...
    )


Features
------------

* Use cases
* Events
* Models
* Views
* Testing

Running Tests
-------------

Does the code actually work?

Prepare test env

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements_test.txt


Run tests

::

    (myenv) $ make test

Run tests in several python versions using tox

::

    (myenv) $ make test-all


Run tests getting code coverage


::

    (myenv) $ make coverage


Generate documentation
----------------------

::

    (myenv) $ pip install -r requirements_dev.txt
    (myenv) $ make docs


.. |build-status| image:: https://travis-ci.org/ontruck/django-ontruck.svg?branch=master
    :target: https://travis-ci.org/ontruck/django-ontruck

.. |coverage| image:: https://codecov.io/gh/ontruck/django-ontruck/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/ontruck/django-ontruck

.. |license| image:: https://img.shields.io/pypi/l/celery.svg
    :alt: BSD License
    :target: https://opensource.org/licenses/BSD-3-Clause
