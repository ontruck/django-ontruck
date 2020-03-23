import inspect

from django.core.management.base import BaseCommand
from django.apps import apps

from django_ontruck.events import EventBase


class Command(BaseCommand):
    help = "Show events info"

    def handle(self, *args, **options):
        events = EventBase.__subclasses__()
        registered_apps = apps.get_app_configs()
        for app in registered_apps:
            found = False
            modules = [m[1].__name__ for m in inspect.getmembers(app.module) if inspect.ismodule(m[1])]
            for e in events:
                if any(e.__module__.startswith(module) for module in modules):
                    if not found:
                        self.stdout.write('[{}]:'.format(self.style.WARNING(app.name)))
                        found = True
                    self.stdout.write(' * {} -> {}'.format(self.style.SUCCESS(e.__name__), e.signal.providing_args))
                    for receiver in e.signal.receivers:
                        _, receiver = receiver
                        func = receiver()
                        self.stdout.write('   - {}.{}'.format(self.style.ERROR(inspect.getsourcefile(func)),
                                                              self.style.ERROR(func.__qualname__)))
