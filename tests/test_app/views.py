from django_ontruck.views import OntruckDelViewSet, OntruckViewSet, OntruckUseCaseViewSet

from .models import FooModel
from .serializers import FooSerializer
from .use_cases import FooUseCase


class FooOntruckViewSet(OntruckViewSet):
    serializer_class = FooSerializer
    queryset = FooModel.objects.all()


class FooOntruckDelViewSet(OntruckDelViewSet):
    serializer_class = FooSerializer
    queryset = FooModel.objects.all()


class FooOntruckUseCaseViewSet(OntruckUseCaseViewSet):
    serializer_class = FooSerializer
    queryset = FooModel.objects.all()
    use_case_creation_class = FooUseCase


