Orwellian
=========
|unittests| |coverage|

Validate all kinds of structured data, with just Python!

How?
----

Orwellian uses Python ``dataclass``-es and ``descriptor``-s to provide
a highly customisable framework for validation.

Example
-------

.. code-block:: python

   @dataclass
   class choice:
       opt: str = field(default=OneOf(["foo", "bar", "baz"]))

   choice(opt="foo")  # valid
   choice(opt=3)  # TypeError
   choice(opt="fo")  # ValueError

.. |unittests| image:: https://github.com/suvayu/orwellian/actions/workflows/python-tests.yml/badge.svg
   :target: https://github.com/suvayu/orwellian/actions/workflows/python-tests.yml

.. |coverage| image:: https://codecov.io/gh/suvayu/orwellian/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/suvayu/orwellian
