import wlc

from django.core.cache import cache
from django_weblate import settings
from django.db.models import Model
from django_weblate.collectors import DjangoModelCollector

from . import models


def get_translation(model: Model, language: str = "en", provider: str = "default"):
    """

    :param model:
    :param language:
    :param provider: string, Reserved for future multi-source configuration
    :return:
    """
    # TODO: Cache it
    cache_key = f'weblate-{provider}-{model._meta.app_label}-{model._meta.model_name}-{model.pk}-{language}'
    result = cache.get(cache_key)
    if result:
        return result

    url = settings.PROVIDERS[provider]["URL"]
    token = settings.PROVIDERS[provider]["TOKEN"]
    weblate = wlc.Weblate(key=token, url=url)

    q = f"key:{settings.PREFIX}{model._meta.app_label}/{model._meta.model_name}/{model.pk} AND language:{language}"
    result = {}
    for unit in weblate.list_units("/units/", params={"q": q}):
        target = "".join(unit.target)
        result[unit.context] = target

    cache.set(cache_key, result, 60 * 10)
    return result


def update_source_translation(key: str, source: str, provider: str = "default"):
    if not source:
        return

    key = key.strip().lower()
    url = settings.PROVIDERS[provider]["URL"]
    token = settings.PROVIDERS[provider]["TOKEN"]
    project = settings.PROVIDERS[provider]["PROJECT"]
    component = settings.PROVIDERS[provider]["COMPONENT"]
    language = settings.PROVIDERS[provider]["SOURCE_LANGUAGE"]
    weblate = wlc.Weblate(key=token, url=url)

    # Load Component
    component: wlc.Component = weblate.get_component(f"{project}/{component}")

    try:
        unit = weblate.add_source_string(
            project=project,
            component=component["name"],
            msgid=key,
            msgstr=source,
            source_language=language,
        )
        unit_url = unit.pop("url")
        unit = wlc.Unit(weblate, unit_url, **unit)
    except wlc.WeblateException:
        q = f"key:{key} AND language:{language}"
        units = weblate.list_units("/units/", params={"q": q})
        unit = next(units)
        if unit["url"] != unit["source_unit"]:
            raise Exception("Inconsistent Unit State")
        unit.update(source=[source])

    instance, created = models.UnitCache.objects.get_or_create(
        provider="default",
        weblate_id=unit.id,
        key=key,
    )
    instance.target = source
    instance.state = unit.state
    instance.source_unit_id = int(unit.source_unit.rstrip("/").split("/")[-1])
    instance.translation = unit.translation


def update_source_translation_by_instance(instance: Model):
    collector = DjangoModelCollector(instance)
    collector.collect()
    for key, source in collector.result:
        update_source_translation(key, source)
