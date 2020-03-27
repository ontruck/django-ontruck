import os

import django_ontruck
from django.core.management.templates import TemplateCommand


class Command(TemplateCommand):
    help = (
        "Creates a Django app directory structure for the given app name in "
        "the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide an application name."

    def handle(self, **options):
        app_name = options.pop('name')
        target = options.pop('directory')
        options['template'] = os.path.join(django_ontruck.__path__[0], 'conf', 'ontruck_app_template')
        super().handle('app', app_name, target, **options)
