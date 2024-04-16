from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404


def index(request):
    from .models import Post
    from django.core.mail import send_mail
    from django.conf import settings
    '''send_mail(
    "Django app",
    "Welcome to django app",
    settings.EMAIL_HOST_USER,
    ["pasternakmary08@gmail.com"],
        fail_silently = False,)'''
    posts=Post.objects.all()
    context={'posts': posts}

    if request.method=='POST':
        from django.contrib.auth.models import User, Group

        search_data = request.POST.get('search')
        if search_data:
            if "#" in search_data:
                posts=Post.objects.filter(content__contains=search_data).all()
                context['posts']=posts
            else:
                users = User.objects.filter(username__contains=search_data).all()
                print(users)
                context['users']=users


        user_id=request.POST.get('user-id')
        print(user_id, "banned")
        if user_id:
            user = User.objects.filter(id=user_id).first()
            if user and request.user.is_staff:
                group, ok= Group.objects.get_or_create(name="users")
                group.user_set.remove(user)


    return render(request, 'blog/index.html', context=context)


@login_required(login_url='/login')
@permission_required('blog.add_post', login_url='/login', raise_exception=True)
def postcreation(request):
    from .form import PostCreationForm

    form = PostCreationForm()
    if request.method == 'POST':
        form = PostCreationForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            print(new_post)
            subscribers=request.user.profile.subscribers.all()
            send_email_notification(request, subscribers, new_post)
            return redirect('homepage')
    return render(request, 'blog/creationform.html', {'form': form})

def send_email_notification(request, users, new_post):
    from django.template.loader import render_to_string
    from django.contrib.sites.shortcuts import get_current_site

    from django.utils.html import strip_tags
    from django.core.mail import send_mail
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives

    subject='You get new post!'

    message=render_to_string('blog/notification.html', {
        'domain': get_current_site(request).domain,
        'protocol': 'https' if request.is_secure() else 'http',
        'new_post': new_post
    })

    html_message = strip_tags(message)

    user_emails=[user.email for user in users]

    email = EmailMultiAlternatives(subject, html_message, to=user_emails)
    email.attach_alternative(message, 'text/html')
    if email.send():
        print('successfully sent')
    else:
        print('error')

@login_required(login_url='/login')
def update_post(request, post_id: int):
    from .form import PostCreationForm
    from django.http import Http404
    from django.forms.models import model_to_dict
    from .models import Post
    from django.shortcuts import get_object_or_404

    #post_id=request.GET.get('id') or request.POST.get('id')
    post = get_object_or_404(Post, pk=int(post_id))

    # if post.author != request.user:
    #     raise Http404("You don't have Post with provided id!")


    form = PostCreationForm(initial=model_to_dict(post))

    if request.method == 'POST':
        form = PostCreationForm(request.POST)
        if form.is_valid():
            post.title=form.cleaned_data['title']

            post.content=form.cleaned_data['content']
            post.save()

            print('updated post', post)
            return redirect('homepage')

    return render(request, 'blog/creationform.html', {'form':form, 'post_id':post.id})


    return render(request,  "blog/creationform.html", {'form': form})

def post_details(request, post_id):
    from .models import Post, Comment
    from .form import CommentCreationForm

    form = CommentCreationForm()
    post=get_object_or_404(Post, pk=int(post_id))
    comments=Comment.objects.filter(post_id=post).all()

    return render(request, 'blog/details.html', {'post': post, 'form': form, 'comments':comments})

def show_post(request):
    from .models import Post, Comment
    from .form import CommentCreationForm
    from django.shortcuts import get_object_or_404
    post=get_object_or_404(Post, pk = int(id))
    form = CommentCreationForm(request.POST)
    comment = Comment.objects.filter(post_id=post).all()

def save_comment(request, post_id):
    from .models import Post
    from .form import CommentCreationForm
    from django.template.loader import render_to_string
    if request.method=='POST':
        form = CommentCreationForm(request.POST)
        post=get_object_or_404(Post, pk=int(post_id))
        if form.is_valid():
            print('new comment saved')
            comment = form.save(commit=False)
            comment.post_id=post
            comment.author=request.user
            comment.save()

            html=render_to_string('blog/comment_template.html', {'comment':comment})

            return JsonResponse({'status':'success', 'html':html})
    return JsonResponse({'status':'failed', 'error':'invalid data'})


@login_required(login_url='/login')
def delete_post(request, id: int):
    from .models import Post
    from django.shortcuts import get_object_or_404
    if request.method=='DELETE':
        post=get_object_or_404(Post, pk=id)
        post.delete()
        return JsonResponse({'status':'success'})

    return JsonResponse({'status':'failed'}, status=400)