from django.conf import settings
from django.utils import translation


class UserLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = settings.LANGUAGE_CODE

        if request.user.is_authenticated:
            user_locale = getattr(request.user, "locale", None)
            if user_locale:
                language = user_locale

        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

        response = self.get_response(request)
        translation.deactivate()
        return response
