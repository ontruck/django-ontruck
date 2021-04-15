from django_ontruck import notifiers as module


class CustomerIOLocMemClient(object):
    __slots__ = ('api_key', )

    def __init__(self, api_key, *args, **kwargs):
        self.api_key = api_key
        if not hasattr(module, 'customerio_outbox'):
            module.customerio_outbox = []

    def send_email(self, request):
        return module.customerio_outbox.append(request)
