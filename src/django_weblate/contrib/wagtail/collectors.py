from django.db.models import Model

from django_weblate.contrib.wagtail.observers import BaseWagtailStreamObserver
from django_weblate import settings


class WagtailStreamValueCollector(BaseWagtailStreamObserver):
    def __init__(self, model: Model, field):
        self.model = model
        self.field = field
        self.result = []
        super().__init__(getattr(model, field))

    def needs_translation(self, block, name=None):
        if name:
            f = settings.TRANSLATE_FIELDS_NAME
            return name in set(getattr(block, f, []) + getattr(block.meta, f, []))
        else:
            f = settings.TRANSLATE_NAME
            return getattr(block, f, False) or getattr(block.meta, f, False)

    def handle_scalar_value(self, parent, value, **kwargs):
        meta = self.model._meta
        name = kwargs.get("name") or ""
        path = f"{settings.PREFIX}{meta.app_label}/{meta.model_name}/{self.model.pk}/{self.field}/{parent.id}/{name}".lower()
        if self.needs_translation(parent.block, name):
            self.result.append((path, value))
