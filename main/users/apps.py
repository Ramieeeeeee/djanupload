from django.apps import AppConfig
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib import messages


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        user_signed_up.connect(allauth_signup)

#@receiver(user_signed_up)
def allauth_signup(request,user, **kwargs):
    from .models import Profile
    from django.contrib.auth.models import Group
    #messages.info(request, user)
    profile=Profile(user=user)
    profile.save()
    print(profile)

    group, ok=Group.objects.get_or_create(name="users")
    group.user_set.add(user)
