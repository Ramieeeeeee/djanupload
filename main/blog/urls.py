from django.shortcuts import render
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='homepage'),
    path('home', views.index, name='homepage'),
    path('posts/update/<int:post_id>', views.update_post, name='updating_post'),
    path('posts/create', views.postcreation, name='creating_post'),
    path('posts/delete/<int:id>', views.delete_post, name='deleting_post'),
    path('posts/comment/<int:post_id>', views.save_comment, name='comment_saving'),
    path('posts/details/<int:post_id>', views.post_details, name='comment_post')
]