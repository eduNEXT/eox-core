#!/usr/bin/env python
# -*- coding: utf-8 -*-
from openedx.core.storage import ProductionStorage, DevelopmentStorage


def get_edxapp_production_staticfiles_storage():
    """
    Return the edx-platform production staticfiles storage
    """
    return ProductionStorage


def get_edxapp_development_staticfiles_storage():
    """
    Return the edx-platform development staticfiles storage
    """
    return DevelopmentStorage
