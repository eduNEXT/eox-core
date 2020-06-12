#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open("README.rst", "r") as fh:
    README = fh.read()

def get_version(*file_paths):
    """Retrieves the version from the main app __init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

version = get_version("eox_core", "__init__.py")


setup(
    name="eox-core",
    version=version,
    author="eduNEXT",
    author_email="contact@edunext.co",
    url="https://github.com/eduNEXT/eox-core",
    description="eduNEXT Openedx extensions",
    long_description=README,
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        "celery",
        "django",
        "djangorestframework",
        "edx-opaque-keys[django]",
    ],
    extras_require={
        "sentry": ["sentry-sdk==0.14.3"],
        "tpa": ["social-auth-core[openidconnect]"],
    },
    scripts=[],
    license="AGPL",
    platforms=["any"],
    zip_safe=False,
    packages=['eox_core'],
    include_package_data=True,
    entry_points={
        "lms.djangoapp": [
            "eox_core = eox_core.apps:EoxCoreConfig",
        ],
        "cms.djangoapp": [
            "eox_core = eox_core.apps:EoxCoreCMSConfig",
        ],
    }
)
