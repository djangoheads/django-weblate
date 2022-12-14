from django.conf import settings as s


def normalize_providers(conf, default):
    for provider, provider_conf in conf.items():
        conf[provider] = dict(list(default.items()) + list(conf[provider].items()))
    return conf


DEFAULT_PROVIDER = {
    "URL": None,
    "TOKEN": None,
    "PROJECT": "Django",
    "COMPONENT": "Content",
    "SOURCE_LANGUAGE": "en",
}

PROVIDERS = normalize_providers(
    getattr(s, "WEBLATE_PROVIDERS", {"default": DEFAULT_PROVIDER}), DEFAULT_PROVIDER
)

TRANSLATE_FIELDS_NAME = getattr(s, "WEBLATE_TRANSLATE_FIELDS_NAME", "translate_fields")
TRANSLATE_NAME = getattr(s, "WEBLATE_TRANSLATE_NAME", "translate")
PREFIX = getattr(s, "WEBLATE_PREFIX", "field://")
