from typing import Any

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField

from django_recaptcha.widgets import ReCaptchaV3, ReCaptchaV2Checkbox


class LoginForm(AuthenticationForm):
    def __int__(self, *args, **kwargs) -> None:
        super(LoginForm, self).__init__(*args, **kwargs)

    captcha=ReCaptchaField(widget=ReCaptchaV2Checkbox())

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(), required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    class Meta:
        model = User
        fields= ['username', 'email', 'password1', 'password2']

class ImageUploadForm(forms.Form):
    image=forms.ImageField(label="Avatar image")


class UpdatePasswordForm(SetPasswordForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
    class Meta:
        model=User
        fields= ['new_password1', 'new_password2']


class ResetPasswordForm(PasswordResetForm):
    username=forms.CharField(label='Username', required=True, min_length=3)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

