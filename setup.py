
from setuptools import setup

setup(
    name="eox-core",
    version="0.0.1",
    author="Edunext",
    author_email="info@edunext.co",
    url="https://github.com/eduNEXT/eox-core",
    description="LTI helper",
    long_description="LTI Helper",
    install_requires=[
        "Django",
    ],
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
