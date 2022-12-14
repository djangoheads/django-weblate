from django.core.management.base import BaseCommand, CommandError

from django_weblate import settings
from django_weblate.weblate import update_source_translation_by_instance


class Command(BaseCommand):
    help = 'Collect content and send to weblate'

    def add_arguments(self, parser):
        parser.add_argument('models', nargs='*', type=str)

    def handle(self, *args, **options):
        handle = []
        candidates = []
        models = options.get("models") or "__all__"
        if isinstance(models, list):
            raise NotImplementedError()

        if models == "__all__":
            import django.apps
            candidates = django.apps.apps.get_models()

        for candidate in candidates:
            if not hasattr(candidate, settings.TRANSLATE_FIELDS_NAME):
                continue
            handle.append(candidate)

        for model in handle:
            for instance in model.objects.all():
                update_source_translation_by_instance(instance)
