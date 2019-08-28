#!/usr/bin/env python
# -*- coding: utf-8 -*-
from eox_core.edxapp_wrapper.storages import (
    get_edxapp_production_staticfiles_storage,
    get_edxapp_development_staticfiles_storage,
)
EdxappProductionStorage = get_edxapp_production_staticfiles_storage()
EdxappDevelopmentStorage = get_edxapp_development_staticfiles_storage()


class AbsoluteUrlAssetsMixin(object):

    def url(self, name):
        """
        Return url of the asset.
        If the asset name is an absolute url, just return the asset name
        """
        if name.startswith("https://") or name.startswith("http://"):
            return name

        return super(AbsoluteUrlAssetsMixin, self).url(name)


class ProductionStorage(AbsoluteUrlAssetsMixin, EdxappProductionStorage):

    pass


class DevelopmentStorage(AbsoluteUrlAssetsMixin, EdxappDevelopmentStorage):

    pass
