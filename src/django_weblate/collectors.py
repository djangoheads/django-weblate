from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
from django_weblate import settings
from django_weblate.contrib.wagtail.collectors import WagtailStreamValueCollector
from wagtail.fields import StreamField


class DjangoModelCollector:
    def __init__(self, model: Model):
        self.model = model
        self.result = []

    def collect_field(self, name):
        meta = self.model._meta
        path = f"{settings.PREFIX}{meta.app_label}/{meta.model_name}/{self.model.pk}/{name}/"
        value = getattr(self.model, name, None)
        self.result.append((path, value))

    def collect(self):
        if hasattr(self.model, settings.TRANSLATE_FIELDS_NAME):
            for field_name in getattr(self.model, settings.TRANSLATE_FIELDS_NAME):
                try:
                    field = self.model._meta.get_field(field_name)
                    if isinstance(field, StreamField):
                        collector = WagtailStreamValueCollector(self.model, field_name)
                        collector.walk()
                        self.result.extend(collector.result)
                    else:
                        self.collect_field(field_name)
                except FieldDoesNotExist:
                    continue
