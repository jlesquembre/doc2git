#from distutils.core import setup
from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), 'rt') as f:
    README = f.read()

setup(name='sphinx2git',
      version='0.1.1',
      author='José Luis Lafuente',
      author_email='jlesquembre@gmail.com',
      description='Helper to commit generated sphinx documentation to git',
      long_description=README,
      license='GNU General Public License v3 (GPLv3)',
      url='http://jlesquembre.github.io/sphinx2git/',
      packages=['sphinx2git'],
      package_data={'src': ['config/*',]},
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        ],
      keywords=['git', 'sphinx'],
      entry_points = {
        'console_scripts': [
            'sphinx2git = sphinx2git.cmdline:main',
            's2g = sphinx2git.cmdline:main',
          ],
        },
      requires=['sarge']
    )
