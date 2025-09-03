from allauth.socialaccount import providers
import pytz
from django.utils import timezone

def account(request):
    return {
        "ACCOUNT_ALLOW_REGISTRATION": True,
    }

def socialaccount(request):
    return {
        "socialaccount_requests": [],
        "socialaccount_providers": [
            {"id": "google", "name": "Google"},
            {"id": "yandex", "name": "Yandex"}
        ]
    }

def timezones(request):
    return {
        'timezones': pytz.common_timezones
    }