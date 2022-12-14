from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
from wagtail.fields import StreamField
from django_weblate import settings
from django_weblate.contrib.wagtail.patcher import WagtailStreamRawDataPatcher


class DjangoModelPatcher:
    def __init__(self, model: Model, translation):
        self.model = model
        self.translation = translation

    def patch_field(self, name):
        meta = self.model._meta
        path = f"{settings.PREFIX}{meta.app_label}/{meta.model_name}/{self.model.pk}/{name}/"
        translation = self.translation.get(path) or self.translation.get(
            path.rstrip("/")
        )
        if not translation:
            return
        setattr(self.model, name, translation)

    def patch(self):
        if hasattr(self.model, "translate_fields"):
            for field_name in self.model.translate_fields:
                try:
                    field = self.model._meta.get_field(field_name)
                    if isinstance(field, StreamField):
                        WagtailStreamRawDataPatcher(
                            self.model, field_name, self.translation
                        ).patch()
                    else:
                        self.patch_field(field_name)
                except FieldDoesNotExist:
                    continue
