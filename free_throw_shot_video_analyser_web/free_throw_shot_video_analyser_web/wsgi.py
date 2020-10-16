"""
WSGI config for free_throw_shot_video_analyser_web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'free_throw_shot_video_analyser_web.settings')

application = get_wsgi_application()
