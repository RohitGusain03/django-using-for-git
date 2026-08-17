from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Comment, Category
from .forms import PostForm, CommentForm


def home(request):

    query = request.GET.get("q", "")

    posts = Post.objects.all().order_by("-created_at")

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    paginator = Paginator(posts, 5)

    page_number = request.GET.get("page")

    posts = paginator.get_page(page_number)

    context = {
        "title": "TechBlog",
        "posts": posts,
        "query": query,
    }

    return render(request, "home.html", context)


def post_details(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    comments = post.comments.all().order_by("-created_at")

    if request.method == "POST":

        if request.user.is_authenticated:

            form = CommentForm(request.POST)

            if form.is_valid():

                comment = form.save(commit=False)

                comment.post = post

                comment.author = request.user

                comment.save()

                messages.success(
                    request,
                    "Comment added successfully."
                )

                return redirect("post_detail", post_id=post.id)

        else:

            messages.error(
                request,
                "Please login to comment."
            )

            return redirect("login")

    else:

        form = CommentForm()

    context = {
        "post": post,
        "comments": comments,
        "form": form,
    }

    return render(request, "post_detail.html", context)


@login_required
def create_post(request):

    if request.method == "POST":

        form = PostForm(request.POST, request.FILES)

        if form.is_valid():

            post = form.save(commit=False)

            post.author = request.user

            post.save()

            messages.success(
                request,
                "Post created successfully."
            )

            return redirect("home")

    else:

        form = PostForm()

    return render(
        request,
        "create_post.html",
        {
            "form": form
        }
    )


@login_required
def edit_post(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
        author=request.user
    )

    if request.method == "POST":

        form = PostForm(
            request.POST,
            request.FILES,
            instance=post
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Post updated successfully."
            )

            return redirect("home")

    else:

        form = PostForm(instance=post)

    return render(
        request,
        "create_post.html",
        {
            "form": form
        }
    )


@login_required
def delete_post(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
        author=request.user
    )

    if request.method == "POST":

        post.delete()

        messages.success(
            request,
            "Post deleted successfully."
        )

        return redirect("home")

    return render(
        request,
        "delete_post.html",
        {
            "post": post
        }
    )


@login_required
def delete_comment(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id,
        author=request.user
    )

    post_id = comment.post.id

    comment.delete()

    messages.success(
        request,
        "Comment deleted successfully."
    )

    return redirect("post_detail", post_id=post_id)

def category_posts(request, category_id):

    category = get_object_or_404(Category, id = category_id)

    posts = Post.objects.filter(
        category = category
    ).order_by("-created_at")

    context = {
        "category": category,
        "posts": posts,
    }
    return render(request, "category_posts.html", context)