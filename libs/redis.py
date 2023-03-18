# -*- coding:utf-8 -*-
from django.conf import settings


def _get_redis_client():
    if "/tmp/" in settings.REDIS_URI:
        from redislite import Redis

        return Redis(settings.REDIS_URI, decode_responses=True)
    else:
        from redis import StrictRedis

        return StrictRedis.from_url(settings.REDIS_URI, decode_responses=True)


rds = _get_redis_client()
