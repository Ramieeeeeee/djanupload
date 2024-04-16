from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls.static import static

from django.conf import settings


from . import views
urlpatterns = ([
    path('signup', views.signup, name='singup'),
    path('profile/<slug:slug>', views.profile, name='profile'),
    path('activate/<uid>/<token>', views.activate_user, name='activate_user'),
    path('logout', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('profile/password/change', views.change_password, name='change_user_password'),

    path('subscribe', views.subscribe, name='subscribe'),

    path('accounts/social/signup/', views.social_signup, ),

    path('profile/password/reset', views.reset_password, name='reset_user_password'),
    path('profile/password/reset/<uid>/<token>', views.reset_password_confirm, name='reset_user_password_confirm'),

               ]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
               )

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)