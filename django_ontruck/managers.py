from django.db.models import Manager


class BaseManager(Manager):

    def __init__(self, *args, include_deleted=False, **kwargs):
        self.include_deleted = include_deleted
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.include_deleted:
            return queryset

        return queryset.filter(deleted=False)
