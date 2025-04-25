"""
Settings for smarteq project.
By default, this imports development settings.
To use production settings, set DJANGO_SETTINGS_MODULE=config.settings.production
"""

import os

# Load development settings by default
# For production, set environment variable: DJANGO_SETTINGS_MODULE=config.settings.production
if os.environ.get('DJANGO_SETTINGS_MODULE') != 'config.settings.production':
    from .development import *  # noqa