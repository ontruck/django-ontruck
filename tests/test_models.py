#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pytest import fixture, mark

from django.contrib.auth.models import User

from django_ontruck import models

from .test_app.models import FooModel


class TestModels:

    @mark.django_db
    def test_private_soft_delete(self, foo_model, user):
        foo_model._soft_delete(deleted_by=user)
        assert foo_model.deleted is True
        assert foo_model.deleted_at is not None
        assert foo_model.deleted_by == user

    @mark.django_db
    def test_soft_delete(self, foo_model, user):
        FooModel.soft_delete([foo_model.id], deleted_by=user)
        foo_model.refresh_from_db()
        assert foo_model.deleted is True
        assert foo_model.deleted_at is not None
        assert foo_model.deleted_by == user

