from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), 'rt') as f:
    README = f.read()

setup(name='doc2git',
      version='0.1.0',
      author='José Luis Lafuente',
      author_email='jlesquembre@gmail.com',
      description='Helper to commit generated documents to git',
      long_description=README,
      license='GNU General Public License v3 (GPLv3)',
      url='http://jlesquembre.github.io/doc2git/',
      packages=['doc2git'],
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
      keywords=['git', 'documentation'],
      entry_points = {
        'console_scripts': [
            'doc2git = doc2git.cmdline:main',
            'd2g = doc2git.cmdline:main',
          ],
        },
      install_requires=['sarge']
    )
