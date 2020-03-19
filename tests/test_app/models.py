from django.db import models

from django_ontruck.models import BaseModel


class FooModel(BaseModel):
    title = models.CharField(max_length=50)
