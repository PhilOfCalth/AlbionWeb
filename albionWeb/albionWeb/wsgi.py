"""
WSGI config for albionWeb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os, sys
# add the hellodjango project path into the sys.path
sys.path.append('~/AlbionWeb/albionWeb')

# add the virtualenv site-packages path to the sys.path
sys.path.append('~/.local/lib/python3.6/site-packages')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'albionWeb.settings.production')

application = get_wsgi_application()
