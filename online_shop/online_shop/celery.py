from __future__ import absolute_import
from __future__ import unicode_literals

import os

from celery import Celery

from online_shop import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "online_shop.settings")

app = Celery("tasks")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.enable_utc = False

app.conf.update(timezone=settings.TIME_ZONE)

app.autodiscover_tasks()
