from django.utils import timezone
from zoneinfo import ZoneInfo

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            timezone.activate(ZoneInfo(request.user.timezone))
        response = self.get_response(request)
        timezone.deactivate()
        return response