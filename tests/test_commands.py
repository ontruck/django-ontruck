from six import StringIO
import shutil
import os
from django.core.management import call_command

class TestCommands:

    def test_show_events(self, mocker):
        mock_stdout = mocker.patch('sys.stdout', new_callable=StringIO)
        call_command('show_events')
        assert "FooEvent -> {'attr1'}" in mock_stdout.getvalue()
        assert "test_app/events/handlers.py.foo_event_handler" in mock_stdout.getvalue()
        assert "[tests.test_app]" in mock_stdout.getvalue()

    def test_startontruckapp(self, mocker):
        app_name = 'some_app'

        if os.path.exists(app_name):
            shutil.rmtree(app_name)

        expected_files = [
            'services.py',
            'use_cases.py',
            'views.py',
            'urls.py',
            '__init__.py',
            'tasks.py',
            'models.py',
            'apps.py',
            'serializers.py',
            'tests/conftest.py',
            'tests/__init__.py',
            'events/__init__.py',
            'events/events.py',
            'events/handlers.py',
            'migrations/__init__.py'
        ]

        call_command('startontruckapp', app_name)

        app_file_paths = []
        for dirname, dirnames, filenames in os.walk(app_name):
            for filename in filenames:
                app_file_paths.append(os.path.join(dirname, filename))

        for expected_filepath in expected_files:
            assert '{}/{}'.format(app_name, expected_filepath) in app_file_paths
        shutil.rmtree(app_name)