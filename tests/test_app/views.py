from django_ontruck.views import (
    OntruckDelViewSet, OntruckViewSet, OntruckUseCaseViewSet,
    NoBrowsableAPIRenderer,
)
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import FooModel
from .serializers import FooSerializer
from .use_cases import FooCreateUseCase, FooUpdateUseCase


class FooOntruckViewSet(OntruckViewSet):
    serializer_class = FooSerializer
    queryset = FooModel.objects.all()

    def get_data_for_create_serializer(self, request, *args, **kwargs):
        data = super(FooOntruckViewSet, self).get_data_for_create_serializer(request, *args, **kwargs)
        pre_serializer = kwargs.get('pre_serializer', None)
        if pre_serializer:
            data['pre_serializer'] = pre_serializer
        return data

    def get_data_for_update_serializer(self, request, *args, **kwargs):
        data = super(FooOntruckViewSet, self).get_data_for_update_serializer(request, *args, **kwargs)
        pre_serializer = kwargs.get('pre_serializer', None)
        if pre_serializer:
            data['pre_serializer'] = pre_serializer
        return data

    def update_serializer_for_create(self, serializer, request):
        super(FooOntruckViewSet, self).update_serializer_for_create(serializer, request)
        serializer.validated_data['extra'] = 'extra_create'

    def update_serializer_for_update(self, serializer, request):
        super(FooOntruckViewSet, self).update_serializer_for_update(serializer, request)
        serializer.validated_data['extra'] = 'extra_update'


class FooOntruckDelViewSet(OntruckDelViewSet):
    serializer_class = FooSerializer
    queryset = FooModel.objects.all()


class FooOntruckUseCaseViewSet(OntruckUseCaseViewSet):
    serializer_class = FooSerializer
    queryset = FooModel.objects.all()
    use_case_creation_class = FooCreateUseCase
    use_case_update_class = FooUpdateUseCase

    def get_data_for_create_serializer(self, request, *args, **kwargs):
        data = super(FooOntruckUseCaseViewSet, self).get_data_for_create_serializer(request, *args, **kwargs)
        pre_serializer = kwargs.get('pre_serializer', None)
        if pre_serializer:
            data['pre_serializer'] = pre_serializer
        return data

    def get_data_for_update_serializer(self, request, *args, **kwargs):
        data = super(FooOntruckUseCaseViewSet, self).get_data_for_update_serializer(request, *args, **kwargs)
        pre_serializer = kwargs.get('pre_serializer', None)
        if pre_serializer:
            data['pre_serializer'] = pre_serializer
        return data

    def get_command_for_create(self, serializer, request):
        command = super(FooOntruckUseCaseViewSet, self).get_command_for_create(serializer, request)
        command['extra'] = 'extra_create_use_case'
        return command

    def get_command_for_update(self, instance, serializer, request):
        command = super(FooOntruckUseCaseViewSet, self).get_command_for_update(instance, serializer, request)
        command['extra'] = 'extra_update_use_case'
        return command


class FooNoBrowsableViewSet(NoBrowsableAPIRenderer, APIView):
    def get(self, request, *args, **kwargs):
        return Response({'browsable': False})

