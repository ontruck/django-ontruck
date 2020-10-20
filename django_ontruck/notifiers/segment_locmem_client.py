from django_ontruck import notifiers as module


class SegmentLocMemClient(object):

    def __init__(self, key, *args, **kwargs):
        self.write_key = key
        if not hasattr(module, 'segment_outbox_identify'):
            module.segment_outbox_identify = []
        if not hasattr(module, 'segment_outbox_track'):
            module.segment_outbox_track = []

    def identify(self, *args, **kwargs):
        return module.segment_outbox_identify.append({'args': args, 'kwargs': kwargs})

    def track(self, *args, **kwargs):
        return module.segment_outbox_track.append({'args': args, 'kwargs': kwargs})
