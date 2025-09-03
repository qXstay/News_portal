import pytz
from django.utils import timezone
from django.utils import translation


class ForceLangMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'django_language' in request.session:
            lang = request.session['django_language']
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
        return self.get_response(request)


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)