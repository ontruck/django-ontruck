import logging
from django_ontruck import notifiers as module

logger = logging.getLogger(__name__)


class SlackLocMemClient(object):

    class SlackLocMemApi(object):

        def post(self, *args, **kwargs):
            module.slack_outbox_api.append({'args': args, 'kwargs': kwargs})

    class SlackLocMemChat(object):

        def post_message(self, *args, **kwargs):
            channel = args[0]
            message = args[1] if len(args) > 1 else kwargs.get('text')
            options = dict(kwargs)
            options.pop('text', None)
            logger.info("SLACK CHAT: %s\n%s\nkwargs = %s", channel, message, options)
            module.slack_outbox_chat.append({'args': args, 'kwargs': kwargs})

    def __init__(self, *args, **kwargs):
        self._api = self.SlackLocMemApi()
        self._chat = self.SlackLocMemChat()
        if not hasattr(module, 'slack_outbox_api'):
            module.slack_outbox_api = []
        if not hasattr(module, 'slack_outbox_chat'):
            module.slack_outbox_chat = []

    @property
    def api(self, *args, **kwargs):
        return self._api

    @property
    def chat(self, *args, **kwargs):
        return self._chat
