#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Storages test backend
"""
from eox_core.test_utils import TestStorage


def get_edxapp_production_staticfiles_storage():  # pylint: disable=invalid-name
    """
    Return the edx-platform production staticfiles storage
    """
    try:
        from openedx.core.storage import ProductionStorage  # pylint: disable=import-outside-toplevel
    except ImportError:
        ProductionStorage = TestStorage
    return ProductionStorage


def get_edxapp_development_staticfiles_storage():  # pylint: disable=invalid-name
    """
    Return the edx-platform development staticfiles storage
    """
    try:
        from openedx.core.storage import DevelopmentStorage  # pylint: disable=import-outside-toplevel
    except ImportError:
        DevelopmentStorage = TestStorage
    return DevelopmentStorage
