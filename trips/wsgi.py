"""
WSGI config for trips project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from dj_static import Cling


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trips.settings")

from django.core.wsgi import get_wsgi_application
application = Cling(get_wsgi_application())
