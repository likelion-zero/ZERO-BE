from django.contrib.auth import get_user_model

User = get_user_model()

class AlwaysSuperUser:
    def authenticate(self, request):
        user = User.objects.filter(is_superuser=True).first()
        return (user, None)