from six import StringIO

from django.core.management import call_command

class TestCommands:

    def test_show_events(self, mocker):
        mock_stdout = mocker.patch('sys.stdout', new_callable=StringIO)
        call_command('show_events')
        assert "FooEvent -> {'attr1'}" in mock_stdout.getvalue()
        assert "test_app/events/handlers.py.foo_event_handler" in mock_stdout.getvalue()
        assert "[tests.test_app]" in mock_stdout.getvalue()
