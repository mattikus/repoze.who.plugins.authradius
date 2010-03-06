##############################################################################
#
# Copyright (c) 2007 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

__version__ = open("version.txt").read()

import os

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

setup(name='repoze.who.plugins.authradius',
      version=__version__,
      description=('Repoze pluggable authentication middleware)'
                   'querying RADIUS back-end for authentication.'),
      long_description=README,
      classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      keywords='web application server wsgi zope',
      author="Chris Shenton",
      author_email="chris@koansys.com",
      url="http://www.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      namespace_packages = ['repoze', 'repoze.who', 'repoze.who.plugins'],
      include_package_data=True,
      zip_safe=False,
      # Isn't there a way to give a dependency_link pointing to an SVN repo?
      # Looks in url for tar.gz distro file:
      dependency_links=['http://dist.repoze.org'],
      tests_require   =['repoze.who', 'pyrad>=1.1'],
      install_requires=['repoze.who', 'pyrad>=1.1'],
      test_suite="repoze.who.plugins.test_authradius",
      entry_points = """
      [paste.filter_app_factory]
      test = repoze.who.plugins.authradius:make_test_middleware
      """
      )

