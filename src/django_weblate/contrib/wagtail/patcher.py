from django.db.models import Model

from django_weblate import settings
from django_weblate.contrib.wagtail.observers import WagtailStreamRawDataObserver


class WagtailStreamRawDataPatcher(WagtailStreamRawDataObserver):
    def __init__(self, model: Model, field: str, translations):
        self.model = model
        self.field = field
        self.translations = translations
        super().__init__(getattr(model, field)._raw_data)

    def handle_scalar(self, parent, value, **kwargs):
        if not isinstance(parent, dict):
            return
        if "id" not in parent:
            return
        meta = self.model._meta
        name = kwargs.get("name") or ""
        path = f"{settings.PREFIX}{meta.app_label}/{meta.model_name}/{self.model.pk}/{self.field}/{parent['id']}/{name}"
        translation = self.translations.get(path)
        if translation is None:
            return

        if name:
            parent["value"][name] = translation
        else:
            parent["value"] = translation

    def patch(self):
        self.walk()
