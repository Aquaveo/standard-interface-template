Best practices
==============

Docstrings
==========

We recommend having docstrings on all classes, modules, public methods and functions, and
on most private methods and functions.
Even if you don't plan on release the documentation to the public,
we find that it helps in navigating the code later when new features are added and
bugs are being fixed.
We use Google style docstrings in this example.

flake
=====

We recommend using flake to check for potential problems in the code, and to keep the
coding style consistent.

Testing
=======

We **strongly** recommend having tests for your model interface. The coverage module allows you
to see how much of your code is touched by your tests. Ideally, your tests should cover 100% of
the code in your interface.

Cython
======

We recommend using Cython for creating a binary distribution of your model interface. Some scripts,
such as the ones in xml_entry_points, should not be cythonized. The XML also should not be cythonized.

CI
==

We recommend using some form of continuous integration testing.

Distribution
============

If you wish to distribute your model interface through Aquaveo, contact sales at Aquaveo_.

.. _Aquaveo: http://www.aquaveo.com.