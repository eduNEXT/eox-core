#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Storages backend
"""
from openedx.core.storage import DevelopmentStorage, ProductionStorage  # pylint: disable=import-error


def get_edxapp_production_staticfiles_storage():  # pylint: disable=invalid-name
    """
    Return the edx-platform production staticfiles storage
    """
    return ProductionStorage


def get_edxapp_development_staticfiles_storage():  # pylint: disable=invalid-name
    """
    Return the edx-platform development staticfiles storage
    """
    return DevelopmentStorage
