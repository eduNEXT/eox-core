from setuptools import setup


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement;
    that is, it is not blank, a comment, or editable.
    """
    # Remove whitespace at the start/end of the line
    line = line.strip()

    # Skip blank lines, comments, and editable installs
    return not (
        line == '' or
        line.startswith('-r') or
        line.startswith('#') or
        line.startswith('-e') or
        line.startswith('git+')
    )


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.
    Returns a list of requirement strings.
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.split('#')[0].strip() for line in open(path).readlines()
            if is_requirement(line)
        )
    return list(requirements)


setup(
    name="eox-core",
    version="0.0.1",
    author="eduNEXT",
    author_email="contact@edunext.co",
    url="https://github.com/eduNEXT/eox-core",
    description="eduNEXT Openedx extensions",
    long_description="",
    install_requires=load_requirements('requirements/base.in'),
    scripts=[],
    license="AGPL",
    platforms=["any"],
    zip_safe=False,
    packages=['eox_core'],
    include_package_data=True,
    entry_points={
        "lms.djangoapp": [
            "plugins = openedx.core.djangoapps.plugins.apps:PluginsConfig",
        ],
        "cms.djangoapp": [
            "plugins = openedx.core.djangoapps.plugins.apps:PluginsConfig",
            "eox_core = eox_core.apps:EoxCoreConfig",
        ],
    }
)
