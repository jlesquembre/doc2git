================================================
 doc2git -- Generate content and push it to git
================================================

doc2git is helper tool to generate static content and push it to a remote git
repository.

============
Introduction
============


Requeriments
------------

doc2git needs `Python <http://python.org>`_ 3.3 or better

Installation
------------

.. code-block:: bash

    pip install doc2git


Basic usage
-----------

In any folder of your git repository run:

.. code-block:: bash

    doc2git


Is also possible run with:

.. code-block:: bash

    d2g


You save 4 characters :-)

.. note::

    Create a file called ``d2g.ini`` in the git repository root folder to tell
    to doc2git what should do, see next section for a better explanation.


Configuration
-------------

This is the default doc2git configuration file:

    ..  literalinclude:: /../../doc2git/config/d2g.ini
        :language: ini

As you can see, default options are for create sphinx documentation and push it
to github, but is possible to overwrite any of this options.


doc2git checks for a ini file called ``d2g.ini`` in your git root repository
folder (the folder with ``.git`` folder). If you want to overwrite the default
cofiguration, be sure that the file name and its location are correct.


For example, if you want to change the commit message, create this file:

.. code-block:: ini

    [git]
    message = My custom message for every documentation commit.


All the other options have the default value, only ``message`` was changed.
