from django import forms
from django.forms.widgets import Textarea
from tinymce.widgets import TinyMCE
from .models import Post, Comment
from django import forms

class PostCreationForm(forms.ModelForm):
    title = forms.CharField(label="Title:", max_length=255)
    content = forms.CharField(label="Content:", widget=TinyMCE(attrs={'placeholder':'When i was a child...', 'class':'mb-4', 'rows': 20}))

    class Meta:
        model=Post
        fields = ['title','content']


class CommentCreationForm(forms.ModelForm):
    content=forms.CharField(widget=Textarea)

    class Meta:
        model = Comment
        fields = ['content']