"""
Settings package for projectfinder.
Defaults to dev settings unless DJANGO_ENV is set to 'prod' or 'production'.
"""
import os

env = os.getenv('DJANGO_ENV', 'dev').lower()
if env in ('prod', 'production'):
    from .prod import *  # noqa: F401, F403
else:
    from .dev import *  # noqa: F401, F403
