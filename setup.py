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


def load_requirements(*requirements_path):
    """
    Load all requirements from the specified requirements files
    Returns a list of requirement strings.
    """
    requirements = set()
    for path in requirements_path:
        with open(path) as reqs:
            requirements.update(
                    line.split('#')[0].strip() for line in reqs
                    if is_requirement(line.strip())
            )

    return list(requirements)


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement;
    that is, it is not blank, a comment, a URL, or an included file.
    """
    return line and not line.startswith(('-r', '#', '-e', 'git+', '-c'))


setup(
    name="eox-core",
    python_requires='>=3.5',
    version=version,
    author="eduNEXT",
    author_email="contact@edunext.co",
    url="https://github.com/eduNEXT/eox-core",
    description="eduNEXT Openedx extensions",
    long_description=README,
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=load_requirements('requirements/base.in'),
    extras_require={
        "sentry": load_requirements('requirements/sentry.in'),
        "tpa": load_requirements('requirements/tpa.in'),
        "eox-audit": load_requirements('requirements/eox-audit-model.in')
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
