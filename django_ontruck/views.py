from django.utils.timezone import now
from rest_framework.pagination import PageNumberPagination, _positive_int
from rest_framework import mixins, viewsets, status, renderers
from rest_framework.response import Response


class NoBrowsableAPIRenderer:
    def get_renderers(self):
        """
        Remove Browsable API renderer if user is no staff.
        """
        rends = self.renderer_classes
        if self.request and self.request.user and self.request.user.is_staff:
            rends.append(renderers.BrowsableAPIRenderer)
        else:
            if renderers.BrowsableAPIRenderer in rends:
                rends.remove(renderers.BrowsableAPIRenderer)
        return [renderer() for renderer in rends]


class OntruckPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    #  Copied from DRF source code to use strict=False and get page_size=0 as deactivated pagination behaviour
    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param], strict=False, cutoff=self.max_page_size)
            except (KeyError, ValueError):
                pass
        return self.page_size


class OntruckCreateMixin(mixins.CreateModelMixin):

    def get_data_for_create_serializer(self, request, *args, **kwargs):
        return request.data

    def update_serializer_for_create(self, serializer, request):
        serializer.validated_data['created_by'] = request.user
        serializer.validated_data['modified_by'] = request.user

    def create(self, request, *args, **kwargs):
        data = self.get_data_for_create_serializer(request, *args, **kwargs)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.update_serializer_for_create(serializer, request)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OntruckUseCaseCreateMixin(mixins.CreateModelMixin):
    use_case_creation_class = None

    @property
    def use_case_creation(self):
        if self.use_case_creation_class is None:
            raise NotImplementedError("Missing use_case_creation_class definition")
        return self.use_case_creation_class()

    def get_command_for_create(self, serializer, request):
        command = serializer.validated_data.copy()
        command['created_by'] = command['modified_by'] = request.user
        return command

    def get_data_for_create_serializer(self, request, *args, **kwargs):
        return request.data

    def create(self, request, *args, **kwargs):
        data = self.get_data_for_create_serializer(request, *args, **kwargs)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        command = self.get_command_for_create(serializer, request)
        response = self.use_case_creation.execute(command, executed_by=request.user)
        serializer = self.get_serializer(instance=response)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OntruckUpdateMixin(mixins.UpdateModelMixin):

    def get_data_for_update_serializer(self, request, *args, **kwargs):
        return request.data

    def update_serializer_for_update(self, serializer, request):
        serializer.validated_data['modified_by'] = request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = self.get_data_for_update_serializer(request, *args, **kwargs)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.update_serializer_for_update(serializer, request)
        self.perform_update(serializer)
        return Response(serializer.data)


class OntruckUseCaseUpdateMixin(mixins.UpdateModelMixin):
    use_case_update_class = None

    def get_data_for_update_serializer(self, request, *args, **kwargs):
        return request.data

    @property
    def use_case_update(self):
        if self.use_case_update_class is None:
            raise NotImplementedError("Missing use_case_update_class definition")
        return self.use_case_update_class()

    def get_command_for_update(self, instance, serializer, request):
        command = serializer.validated_data.copy()
        command['instance'] = instance
        command['modified_by'] = request.user
        return command

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = self.get_data_for_update_serializer(request, *args, **kwargs)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        command = self.get_command_for_update(instance, serializer, request)
        response = self.use_case_update.execute(command, executed_by=request.user)
        serializer = self.get_serializer(instance=response)
        return Response(serializer.data)


class OntruckDeleteMixin(mixins.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.deleted = True
        obj.deleted_at = now()
        obj.deleted_by = request.user
        obj.modified_by = request.user
        obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OntruckReadViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet
                         ):
    """
    A master viewset with all read mixins
    """
    pagination_class = OntruckPagination


class OntruckListViewSet(mixins.ListModelMixin,
                         viewsets.GenericViewSet
                         ):
    """
    A master viewset with all read mixins
    """
    pagination_class = OntruckPagination


class OntruckCreateReadViewSet(OntruckCreateMixin,
                               OntruckReadViewSet
                               ):
    """
    A viewset with retrieve, list and create
    """
    pass


class OntruckUpdateReadDeleteViewSet(OntruckUpdateMixin,
                                     OntruckDeleteMixin,
                                     OntruckReadViewSet
                                     ):
    """
    A viewset with retrieve, list, update, partial_update and destroy
    """
    pass


class OntruckViewSet(OntruckCreateMixin,
                     OntruckUpdateMixin,
                     OntruckReadViewSet
                     ):
    """
    A master viewset with all mixins of ModelViewSet except for delete
    """
    pass


class OntruckUseCaseViewSet(OntruckUseCaseCreateMixin,
                            OntruckUseCaseUpdateMixin,
                            OntruckReadViewSet
                            ):
    pass


class OntruckDelViewSet(OntruckDeleteMixin, OntruckViewSet):
    """
    Insure the objects have deleted and deleted_at fields
    """
    pass


class OntruckUseCaseDelViewSet(OntruckDeleteMixin, OntruckUseCaseViewSet):
    """
    Insure the objects have deleted and deleted_at fields
    """
    pass


class OntruckUpdateViewSet(OntruckUpdateMixin, viewsets.GenericViewSet):
    """
    Create relationships between existent resources
    """
    pass


class OntruckWriteViewSet(OntruckCreateMixin, OntruckUpdateMixin, viewsets.GenericViewSet):
    """
    Write Only viewset, mainly for the ManualShipment
    """
    pass


class OntruckCreateViewSet(OntruckCreateMixin, viewsets.GenericViewSet):
    """
    Create Only viewset, mainly for the FullQuote
    """
    pass
