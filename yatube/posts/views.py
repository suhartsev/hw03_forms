from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.core.paginator import Paginator

from .forms import PostForm
from .models import Post, Group, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'posts/index.html',
        {'page_obj': page_obj}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'posts/group_list.html',
        {'group': group, 'page_obj': page_obj}
    )


def profile(request, username):
    user_author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user_author)
    paginator = Paginator(post_list, settings.LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_number = post_list.count()
    context = {
        'post_list': post_list,
        'page_obj': page_obj,
        'post_number': post_number,
        'author': user_author,
    }
    return render(
        request,
        'posts/profile.html',
        context
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_number = Post.objects.select_related('author').filter(
        author=post.author
    ).count()
    context = {
        'post': post,
        'post_number': post_number,
    }
    return render(
        request,
        'posts/post_detail.html',
        context
    )


def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(
                'posts:profile',
                post.author.username
            )
    form = PostForm()
    return render(
        request,
        'posts/create_post.html',
        {'form': form}
    )


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if post.author == request.user:
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post.pk)
        form = PostForm(instance=post)
        return render(
            request,
            "posts/create_post.html",
            {'form': form, "is_edit": is_edit}
        )
    else:
        return redirect('posts:post_detail', post.pk)
