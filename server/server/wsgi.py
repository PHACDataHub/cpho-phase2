"""
WSGI config for cphophase2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

# setting DJANGO_SETTINGS_MODULE usually occurs here, but has been moved to gunicorn.conf.py's post_fork hook

application = get_wsgi_application()
