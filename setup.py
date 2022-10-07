"""
Setup file for eox_core Django plugin.
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from setuptools import setup


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

VERSION = get_version("eox_core", "__init__.py")


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.
    Returns:
        list: Requirements file relative path strings
    """
    requirements = set()
    for path in requirements_paths:
        with open(path, 'r', encoding='utf-8') as requirements_file:
            requirements.update(
                line.split('#')[0].strip() for line in requirements_file.readlines()
                if is_requirement(line.strip())
            )
    return list(requirements)


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement.
    Returns:
        bool: True if the line is not blank, a comment, a URL, or
              an included file
    """
    return line and not line.startswith(('-r', '#', '-e', 'git+', '-c'))


setup(
    name="eox-core",
    python_requires='>=3.8',
    version=VERSION,
    author="eduNEXT",
    author_email="contact@edunext.co",
    url="https://github.com/eduNEXT/eox-core",
    description="eduNEXT Openedx extensions",
    long_description=README,
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 3.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.10',
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
