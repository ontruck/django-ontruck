import logging
from django_ontruck import notifiers as module

logger = logging.getLogger(__name__)


class SlackLocMemClient(object):
    class SlackLocMemApi(object):
        def post(self, *args, **kwargs):
            caller = getattr(module, 'slack_outbox_api')
            caller.append({'args': args, 'kwargs': kwargs})

    class SlackLocMemChat(object):
        def post_message(self, *args, **kwargs):
            channel = args[0]
            message = args[1] if len(args) > 1 else kwargs.get('text')
            options = dict(kwargs)
            options.pop('text', None)
            logger.info("SLACK CHAT: %s\n%s\nkwargs = %s", channel, message, options)

            caller = getattr(module, 'slack_outbox_chat')
            caller.append({'args': args, 'kwargs': kwargs})

    def __init__(self, *args, **kwargs):
        self._api = self.SlackLocMemApi()
        self._chat = self.SlackLocMemChat()

        api_attr = 'slack_outbox_api'
        chat_attr = 'slack_outbox_chat'

        if not hasattr(module, api_attr):
            setattr(module, api_attr, [])
        if not hasattr(module, chat_attr):
            setattr(module, chat_attr, [])

    @property
    def api(self, *args, **kwargs):
        return self._api

    @property
    def chat(self, *args, **kwargs):
        return self._chat
