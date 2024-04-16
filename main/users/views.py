from email.message import EmailMessage

from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
# from django.contrib.auth.models import login
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .form import LoginForm
from .models import Profile
from django.utils.html import strip_tags
from .token import account_activation_token
from django.contrib import messages


def create_email(request, user, subject: str, html_page: str):
    # subject='Activate your email'
    message = render_to_string(html_page, {'user': user,
                                           'domain': get_current_site(request).domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                           'token': account_activation_token.make_token(user),
                                           'protocol': 'https' if request.is_secure() else 'http'}
                               )

    text_message = strip_tags(message)

    email = EmailMultiAlternatives(subject, text_message, to=[user.email])
    email.attach_alternative(message, 'text/html')
    return email


def activate_user(request, uid, token):
    from .token import account_activation_token
    print('User id:', uid, 'secret token', token)
    try:
        from django.contrib.auth.models import User
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        group, ok = Group.objects.get_or_create(name='users')
        group.user_set.add(user)
        messages.success(request, "Your account has been activated successfully!")
        redirect('/login')
    else:
        messages.success(request, "Invalid activation link")
    return redirect('homepage')


def login(request):
    from django.contrib.auth.forms import AuthenticationForm
    from django.contrib.auth import authenticate, login
    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome <b>{user.username}</b>')
                return redirect('homepage')

        else:
            for key, error in list(form.errors.items()):

                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(request, 'recaptcha invalid')
                    continue
                messages.error(request, error)

    form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def logout(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('homepage')


def signup(request):
    from .form import RegisterForm
    from django.contrib.auth import login
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            print("user")
            profile = Profile(user=user)
            # profile.image=form.cleaned_data.get('image')
            profile.save()
            print("saved")
            email = create_email(
                request,
                user,
                'Activate your user account!',
                'users/activation.html')

            if email.send():
                messages.success(request, 'Check your email and confirm your account!')
            else:
                messages.error(request, 'Something went wrong with your email. Try it later...')

        return redirect('/home')
    return render(request, 'registration/signup.html', {'form': form})


@login_required()
def profile(request, slug):
    from .models import Profile
    from .form import ImageUploadForm
    from django.shortcuts import get_object_or_404

    profile = get_object_or_404(Profile, slug=slug)
    form = ImageUploadForm()
    is_subscribed=True if request.user in profile.subscribers.all() else False
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            profile.image = form.cleaned_data.get('image')
            profile.save()

    return render(request, 'users/profile.html', {'profile': profile, 'form': form, 'is_subscribed': is_subscribed})


@login_required
def subscribe(request):
    from .models import Profile
    from django.http import JsonResponse
    if request.method == 'POST':
        data = dict(request.POST)
        subscriber = request.user
       # print('user has:', subscriber.subscribed_profiles.all())

        author_slug = data.get('author')
        response={}
        if author_slug is not None:
            author = Profile.objects.filter(slug=author_slug[0]).first()
            if author in subscriber.subscribed_profiles.all():
                author.subscribers.remove(subscriber)
                print('removed')
                response['status'] = 'removed'
            else:
                author.subscribers.add(subscriber)
                print('added')
                response['status'] = 'added'
            print('user has:', subscriber.subscribed_profiles.all())
        return JsonResponse(response)
    return JsonResponse({'status': 'error'}), 400


@login_required
def change_password(request):
    from .form import UpdatePasswordForm

    form = UpdatePasswordForm(request.user)
    if request.method == 'POST':
        form = UpdatePasswordForm(request.user, request.POST)
        if request.method == 'POST':
            form = UpdatePasswordForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been changed!')

                return redirect('login')
            else:
                for key, error in list(form.errors.items()):
                    if key == 'captcha' and error[0] == 'This field is required.':
                        messages.error(request, 'Please complete the ReCaptcha!')
                        continue
                    messages.error(request, error)

    return render(request, 'users/change_password.html', {'form': form})

def social_signup(request):
    messages.error(request, 'something went wrong')
    return redirect('homepage')


def reset_password(request):
    from .form import ResetPasswordForm
    form = ResetPasswordForm()
    from django.contrib.auth.models import User

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            user_username = form.cleaned_data.get('username')

            user = User.objects.filter(email=user_email, username=user_username).first()

            if user:
                email = create_email(
                    request,
                    user,
                    'Reset Your Password',
                    'users/password_reset.html'

                )

                if email.send():
                    messages.success(request, "Check your email")
                else:
                    messages.error(request, 'Try it again, something went wrong')
                return redirect('login')

            else:
                messages.error(request, 'User with provided email and username not found!')

    return render(request, 'users/change_password.html', {'form': form})


def reset_password_confirm(request, uid, token):
    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth import login
    from django.utils.encoding import force_str
    from .token import account_activation_token

    try:
        from django.contrib.auth.models import User
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        login(request, user)
        messages.success(request, 'Create new password!')
        return redirect('change_user_password')
