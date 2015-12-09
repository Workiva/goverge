"""goverge PyPI Package."""

import imp
import os
from setuptools import find_packages
from setuptools import setup


def get_version():
    """Get the version of the project."""
    with open('goverge/_pkg_meta.py', 'rb') as fp:
        mod = imp.load_source('_pkg_meta', 'biloba', fp)

        return mod.version


def read(filename):
    """Read file contents."""
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), filename))
    with open(path, 'rb') as f:
        return f.read().decode('utf-8')


setup_args = dict(
    name='goverge',
    version=get_version(),
    description='Go Coverage Tool for multi package coverage reporting.',
    long_description=read('README.md'),
    author='Wesley Balvanz',
    author_email='wesley.balvanz@workiva.com',
    url='https://github.com/Workiva/goverge',
    packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test']),
    entry_points={'console_scripts': ['goverge = goverge.main:main']},
    license=read('LICENSE.txt'))


if __name__ == '__main__':
    setup(**setup_args)
