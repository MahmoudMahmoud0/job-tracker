from django.contrib.auth.backends import ModelBackend


class EmailStatusAwareBackend(ModelBackend):
    def user_can_authenticate(self, user):
        # Let the login form decide whether inactive or unverified users
        # should proceed so we can show a specific recovery action.
        return True
