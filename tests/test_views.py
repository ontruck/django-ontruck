import json

from pytest import mark

from rest_framework import renderers
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from .test_app.views import (
    FooOntruckDelViewSet, FooOntruckViewSet, FooOntruckUseCaseViewSet,
    FooNoBrowsableViewSet,
)
from .test_app.models import FooModel
from django_ontruck.views import OntruckPagination

factory = APIRequestFactory()


class TestViews:

    @mark.django_db
    def test_create_view_set_validation_error(self, user):
        request = factory.post('/', '', content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckViewSet.as_view(actions={
            'post': 'create',
        })

        response = my_view(request)
        assert response.status_code == 400

    @mark.django_db
    def test_create_view_set_ok(self, user):
        request = factory.post('/', json.dumps({'title': 'test_title'}), content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckViewSet.as_view(actions={
            'post': 'create',
        })

        response = my_view(request)
        assert response.status_code == 201
        assert FooModel.objects.count() == 1
        foo_model = FooModel.objects.first()
        assert foo_model.title == 'test_title'
        assert foo_model.created_at is not None
        assert foo_model.modified_at is not None
        assert foo_model.created_by == user
        assert foo_model.modified_by == user
        assert foo_model.extra == 'extra_create'
        assert foo_model.pre_serializer is None

    @mark.django_db
    def test_create_view_set_ok_with_view_kwargs(self, user):
        request = factory.post('/', json.dumps({'title': 'test_title'}), content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckViewSet.as_view(actions={
            'post': 'create',
        })

        response = my_view(request, pre_serializer='pre_serializer_create')
        assert response.status_code == 201
        assert FooModel.objects.count() == 1
        foo_model = FooModel.objects.first()
        assert foo_model.title == 'test_title'
        assert foo_model.created_at is not None
        assert foo_model.modified_at is not None
        assert foo_model.created_by == user
        assert foo_model.modified_by == user
        assert foo_model.extra == 'extra_create'
        assert foo_model.pre_serializer == 'pre_serializer_create'

    @mark.django_db
    def test_update_view_set_validation_error(self, user):
        sample = FooModel.objects.create(title='title')
        request = factory.put('/{}/'.format(sample.id), '', content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckViewSet.as_view(actions={
            'put': 'update',
        })

        response = my_view(request, pk=sample.id)
        assert response.status_code == 400

    @mark.django_db
    def test_update_view_set_ok(self, user):
        sample = FooModel.objects.create(title='title')
        request = factory.put('/{}/'.format(sample.id), json.dumps({'title': 'test_title'}),
                               content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckViewSet.as_view(actions={
            'put': 'update',
        })

        response = my_view(request, pk=sample.id)
        assert response.status_code == 200
        assert FooModel.objects.count() == 1
        foo_model = FooModel.objects.first()
        assert foo_model.title == 'test_title'
        assert foo_model.modified_at is not None
        assert foo_model.modified_by == user
        assert foo_model.extra == 'extra_update'
        assert foo_model.pre_serializer is None

    @mark.django_db
    def test_update_view_set_ok_with_view_kwargs(self, user):
        sample = FooModel.objects.create(title='title')
        request = factory.put('/{}/'.format(sample.id), json.dumps({'title': 'test_title'}),
                               content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckViewSet.as_view(actions={
            'put': 'update',
        })

        response = my_view(request, pk=sample.id, pre_serializer='pre_serializer_update')
        assert response.status_code == 200
        assert FooModel.objects.count() == 1
        foo_model = FooModel.objects.first()
        assert foo_model.title == 'test_title'
        assert foo_model.modified_at is not None
        assert foo_model.modified_by == user
        assert foo_model.extra == 'extra_update'
        assert foo_model.pre_serializer == 'pre_serializer_update'

    @mark.django_db
    def test_delete_view_set_ok(self, user):
        sample = FooModel.objects.create(title='title')
        request = factory.delete('/{}/'.format(sample.id), '', content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckDelViewSet.as_view(actions={
            'delete': 'destroy',
        })

        response = my_view(request, pk=sample.id)
        assert response.status_code == 204
        assert FooModel.objects.count() == 1
        foo_model = FooModel.objects.first()
        assert foo_model.deleted is True
        assert foo_model.deleted_at is not None
        assert foo_model.deleted_by == user

    @mark.django_db
    def test_create_use_case_view_set_ok(self, user):
        request = factory.post('/', json.dumps({'title': 'test_title'}), content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckUseCaseViewSet.as_view(actions={
            'post': 'create',
        })

        response = my_view(request)
        assert response.status_code == 201
        assert FooModel.objects.count() == 1
        foo_model = FooModel.objects.first()
        assert foo_model.title == 'test_title'
        assert foo_model.created_at is not None
        assert foo_model.modified_at is not None
        assert foo_model.created_by == user
        assert foo_model.modified_by == user
        assert foo_model.extra == 'extra_create_use_case'
        assert foo_model.pre_serializer is None

    @mark.django_db
    def test_create_use_case_view_set_ok_with_view_kwargs(self, user):
        request = factory.post('/', json.dumps({'title': 'test_title'}), content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckUseCaseViewSet.as_view(actions={
            'post': 'create',
        })

        response = my_view(request, pre_serializer='pre_serializer_create')
        assert response.status_code == 201
        assert FooModel.objects.count() == 1
        foo_model = FooModel.objects.first()
        assert foo_model.title == 'test_title'
        assert foo_model.created_at is not None
        assert foo_model.modified_at is not None
        assert foo_model.created_by == user
        assert foo_model.modified_by == user
        assert foo_model.extra == 'extra_create_use_case'
        assert foo_model.pre_serializer == 'pre_serializer_create'

    @mark.django_db
    def test_update_use_case_view_set_ok(self, user):
        sample = FooModel.objects.create(title='title')
        request = factory.put('/{}/'.format(sample.id), json.dumps({'title': 'test_title'}),
                               content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckUseCaseViewSet.as_view(actions={
            'put': 'update',
        })

        response = my_view(request, pk=sample.id)
        assert response.status_code == 200
        assert FooModel.objects.count() == 1
        foo_model = FooModel.objects.first()
        assert foo_model.title == 'test_title'
        assert foo_model.modified_at is not None
        assert foo_model.modified_by == user
        assert foo_model.extra == 'extra_update_use_case'
        assert foo_model.pre_serializer is None

    @mark.django_db
    def test_update_use_case_view_set_ok_with_view_kwargs(self, user):
        sample = FooModel.objects.create(title='title')
        request = factory.put('/{}/'.format(sample.id), json.dumps({'title': 'test_title'}),
                               content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckUseCaseViewSet.as_view(actions={
            'put': 'update',
        })

        response = my_view(request, pk=sample.id, pre_serializer='pre_serializer_update')
        assert response.status_code == 200
        assert FooModel.objects.count() == 1
        foo_model = FooModel.objects.first()
        assert foo_model.title == 'test_title'
        assert foo_model.modified_at is not None
        assert foo_model.modified_by == user
        assert foo_model.extra == 'extra_update_use_case'
        assert foo_model.pre_serializer == 'pre_serializer_update'

    @mark.django_db
    def test_pagination(self, user):
        sample = FooModel.objects.create(title='title')
        request = factory.get('/', '', content_type='application/json')
        force_authenticate(request, user=user)
        my_view = FooOntruckUseCaseViewSet.as_view(actions={
            'get': 'list',
        }, pagination_class=OntruckPagination)

        response = my_view(request)
        assert response.status_code == 200

    @mark.django_db
    def test_no_browsable_api(self, user):
        request = factory.get('/', '', content_type='application/json')
        request.user = user

        # If user is not staff, then API should not be browsable
        nobrowsable = FooNoBrowsableViewSet()
        nobrowsable.setup(request)
        nobrowsable_renders = nobrowsable.get_renderers()

        assert not any([isinstance(r, renderers.BrowsableAPIRenderer) for r in nobrowsable_renders])

        # If user is staff, then API should be browsable
        user.is_staff = True
        browsable = FooNoBrowsableViewSet()
        browsable.setup(request)
        browsable_renders = browsable.get_renderers()

        assert any([isinstance(r, renderers.BrowsableAPIRenderer) for r in browsable_renders])
