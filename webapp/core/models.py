from __future__ import unicode_literals

__author__ = 'K2A'
from django.db import models


class UrlMapping(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    deleted_date = models.DateTimeField(null=True, blank=True)
    full_url = models.CharField(max_length=255, unique=True)
    short_url = models.CharField(max_length=255, unique=True)


    class Meta:
        db_table = "tb_url_mapping"

    def __unicode__(self):
        return self.full_url

    @property
    def get_short_url(self):
        return "http://localhost:8000/api/{0}".format(self.short_url)

    def to_json(self):
        return {
            "id": self.id,
            "full_url": self.full_url,
            "short_url": self.get_short_url,
        }
