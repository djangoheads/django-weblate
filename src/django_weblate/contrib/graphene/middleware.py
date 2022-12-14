from django.db.models import Model

from django_weblate.patchers import DjangoModelPatcher
from django_weblate.weblate import get_translation
from django_weblate import settings


class TranslationMiddleware:
    def resolve(self, next, root, info, **args):
        if issubclass(type(root), Model) and hasattr(
            root, settings.TRANSLATE_FIELDS_NAME
        ):
            request = info.context
            language = (
                request.META.get("HTTP_X_ACCEPT_LANGUAGE")
                or request.COOKIES.get("i18n-language")
                or request.META.get("HTTP_ACCEPT_LANGUAGE")
                or "en"
            )
            translation = get_translation(root, language=language)
            DjangoModelPatcher(root, translation).patch()
        return next(root, info, **args)
