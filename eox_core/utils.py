#!/usr/bin/python
"""
Util function definitions.
"""
import hashlib

from django.core import cache

try:
    cache = cache.caches['general']  # pylint: disable=invalid-name
except Exception:  # pylint: disable=broad-except
    cache = cache.cache  # pylint: disable=invalid-name


def fasthash(string):
    """
    Hashes `string` into a string representation of a 128-bit digest.
    """
    md4 = hashlib.new("md4")
    md4.update(string.encode('utf-8'))
    return md4.hexdigest()
