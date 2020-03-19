# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.timezone import now


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   related_name="%(app_label)s_%(class)s_created_set")
    modified_at = models.DateTimeField(auto_now=True, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                    related_name="%(app_label)s_%(class)s_modified_set")
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   related_name="%(app_label)s_%(class)s_deleted_set")

    class Meta:
        abstract = True

    @classmethod
    def soft_delete(cls, ids, deleted_by=None):
        cls.objects.filter(id__in=ids).update(deleted=True, deleted_at=now(), deleted_by=deleted_by)

    def _soft_delete(self, deleted_by=None):
        self.deleted = True
        self.deleted_at = now()
        self.deleted_by = deleted_by
        self.save()
