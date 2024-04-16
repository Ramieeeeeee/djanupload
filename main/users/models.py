from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    image=models.ImageField(upload_to='profile_images', default='profile_icon.jpg')
    #is_active=models.BooleanField(default=False)
    subscribers=models.ManyToManyField(User, related_name='subscribed_profiles')
    slug=models.SlugField(blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
           self.slug=slugify(self.user.username)

        super().save(*args, **kwargs)

