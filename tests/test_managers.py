#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pytest import mark

from .test_app.models import FooModel


class TestBaseManagers:

    @mark.django_db
    def test_base_manager(self, foo_model):
        assert FooModel.objects.count() == 1
        assert FooModel.objects_all.count() == 1
        foo_model._soft_delete()
        assert FooModel.objects.count() == 0
        assert FooModel.objects_all.count() == 1
