from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta

from .models import Post, Comment, Category, PostMedia, Tag, Notification
from .forms import PostForm, CommentForm


POSTS_PER_PAGE = 9


def _notify(recipient, sender, notification_type, post=None):
    """Create a notification unless the actor is the recipient themself."""
    if recipient == sender:
        return
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        post=post,
    )


# ==========================================
# HOME / FEED
# ==========================================

def home(request):

    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "latest")
    category_id = request.GET.get("category", "")

    posts = Post.objects.select_related("author", "author__profile", "category").prefetch_related(
        "tags", "likes", "saved_by", "media"
    )

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(author__username__icontains=query)
        ).distinct()

    if category_id:
        posts = posts.filter(category_id=category_id)

    if sort == "top":
        posts = posts.annotate(like_total=Count("likes", distinct=True)).order_by(
            "-like_total", "-created_at"
        )
    elif sort == "trending":
        since = timezone.now() - timedelta(days=7)
        posts = posts.filter(created_at__gte=since).annotate(
            like_total=Count("likes", distinct=True)
        ).order_by("-like_total", "-created_at")
    elif sort == "following" and request.user.is_authenticated:
        following_ids = request.user.following.values_list("following_id", flat=True)
        posts = posts.filter(author_id__in=following_ids).order_by("-created_at")
    else:
        sort = "latest"
        posts = posts.order_by("-created_at")

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    trending_tags = Tag.objects.annotate(
        post_total=Count("posts")
    ).order_by("-post_total")[:10]

    context = {
        "title": "MemeStack",
        "posts": posts,
        "query": query,
        "sort": sort,
        "categories": Category.objects.all(),
        "selected_category": category_id,
        "trending_tags": trending_tags,
    }

    return render(request, "home.html", context)


# ==========================================
# POST DETAILS
# ==========================================

def post_details(request, post_id):

    post = get_object_or_404(
        Post.objects.select_related("author", "category").prefetch_related("tags", "media"),
        id=post_id
    )

    # simple view counter (skip counting the author's own visits)
    if not request.user.is_authenticated or request.user != post.author:
        Post.objects.filter(pk=post.pk).update(views=post.views + 1)
        post.views += 1

    comments = post.comments.filter(parent__isnull=True).select_related("author").prefetch_related(
        "likes", "replies__author", "replies__likes"
    ).order_by("-created_at")

    if request.method == "POST":

        if request.user.is_authenticated:

            form = CommentForm(request.POST)

            if form.is_valid():

                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user

                parent_id = request.POST.get("parent_id")
                if parent_id:
                    comment.parent = get_object_or_404(Comment, id=parent_id, post=post)
                    _notify(comment.parent.author, request.user, Notification.REPLY, post)
                else:
                    _notify(post.author, request.user, Notification.COMMENT, post)

                comment.save()

                messages.success(request, "Comment added successfully.")

                return redirect("post_detail", post_id=post.id)

        else:

            messages.error(request, "Please login to comment.")
            return redirect("login")

    else:

        form = CommentForm()

    related_posts = Post.objects.filter(
        category=post.category
    ).exclude(id=post.id)[:4] if post.category else Post.objects.exclude(id=post.id)[:4]

    is_following_author = False
    if request.user.is_authenticated and request.user != post.author:
        is_following_author = request.user.following.filter(following=post.author).exists()

    context = {
        "post": post,
        "comments": comments,
        "form": form,
        "related_posts": related_posts,
        "is_following_author": is_following_author,
    }

    return render(request, "post_detail.html", context)


# ==========================================
# CREATE POST
# ==========================================

@login_required
def create_post(request):

    if request.method == "POST":

        form = PostForm(request.POST, request.FILES)

        if form.is_valid():

            post = form.save(commit=False)
            post.author = request.user
            post.save()

            if hasattr(post, "save_tags_m2m"):
                post.save_tags_m2m()

            additional_images = request.FILES.getlist("additional_images")

            for image in additional_images:
                PostMedia.objects.create(post=post, image=image)

            messages.success(request, "Your meme is live! 🎉")

            return redirect("post_detail", post_id=post.id)

    else:

        form = PostForm()

    return render(request, "create_post.html", {"form": form})


# ==========================================
# EDIT POST
# ==========================================

@login_required
def edit_post(request, post_id):

    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == "POST":

        form = PostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():

            form.save()

            additional_images = request.FILES.getlist("additional_images")
            for image in additional_images:
                PostMedia.objects.create(post=post, image=image)

            messages.success(request, "Post updated successfully.")

            return redirect("post_detail", post_id=post.id)

    else:

        form = PostForm(instance=post)

    return render(request, "create_post.html", {"form": form, "post": post})


@login_required
def delete_post_media(request, media_id):

    media = get_object_or_404(PostMedia, id=media_id, post__author=request.user)

    post_id = media.post.id

    if request.method == "POST":
        media.delete()
        messages.success(request, "Image removed.")

    return redirect("edit_post", post_id=post_id)


# ==========================================
# DELETE POST
# ==========================================

@login_required
def delete_post(request, post_id):

    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect("home")

    return render(request, "delete_post.html", {"post": post})


# ==========================================
# LIKE / UNLIKE (AJAX)
# ==========================================

@login_required
def like_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        _notify(post.author, request.user, Notification.LIKE, post)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"liked": liked, "like_count": post.like_count})

    return redirect("post_detail", post_id=post.id)


# ==========================================
# SAVE / UNSAVE (AJAX)
# ==========================================

@login_required
def save_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if post.saved_by.filter(id=request.user.id).exists():
        post.saved_by.remove(request.user)
        saved = False
        message = "Post removed from saved posts."
    else:
        post.saved_by.add(request.user)
        saved = True
        message = "Post saved successfully."

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"saved": saved, "save_count": post.save_count})

    messages.success(request, message)
    return redirect("post_detail", post_id=post.id)


# ==========================================
# SAVED POSTS
# ==========================================

@login_required
def saved_posts(request):

    posts = request.user.saved_posts.select_related("author", "author__profile").prefetch_related(
        "tags", "likes", "saved_by", "media"
    ).order_by("-created_at")

    paginator = Paginator(posts, POSTS_PER_PAGE)
    posts = paginator.get_page(request.GET.get("page"))

    return render(request, "saved_posts.html", {"posts": posts})


# ==========================================
# COMMENT LIKE (AJAX)
# ==========================================

@login_required
def like_comment(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)

    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"liked": liked, "like_count": comment.like_count})

    return redirect("post_detail", post_id=comment.post.id)


# ==========================================
# DELETE COMMENT
# ==========================================

@login_required
def delete_comment(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id, author=request.user)

    post_id = comment.post.id

    comment.delete()

    messages.success(request, "Comment deleted successfully.")

    return redirect("post_detail", post_id=post_id)


# ==========================================
# EDIT COMMENT
# ==========================================

@login_required
def edit_comment(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id, author=request.user)

    if request.method == "POST":

        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():

            form.save()

            messages.success(request, "Comment updated successfully.")

            return redirect("post_detail", post_id=comment.post.id)

    else:

        form = CommentForm(instance=comment)

    return render(request, "edit_comment.html", {"form": form, "comment": comment})


# ==========================================
# CATEGORY POSTS
# ==========================================

def category_posts(request, category_id):

    category = get_object_or_404(Category, id=category_id)

    posts = Post.objects.filter(category=category).select_related(
        "author", "author__profile"
    ).prefetch_related("tags", "likes", "saved_by", "media").order_by("-created_at")

    paginator = Paginator(posts, POSTS_PER_PAGE)
    posts = paginator.get_page(request.GET.get("page"))

    return render(request, "category_posts.html", {"category": category, "posts": posts})


# ==========================================
# TAG POSTS
# ==========================================

def tag_posts(request, slug):

    tag = get_object_or_404(Tag, slug=slug)

    posts = tag.posts.select_related("author", "author__profile").prefetch_related(
        "tags", "likes", "saved_by", "media"
    ).order_by("-created_at")

    paginator = Paginator(posts, POSTS_PER_PAGE)
    posts = paginator.get_page(request.GET.get("page"))

    return render(request, "tag_posts.html", {"tag": tag, "posts": posts})


# ==========================================
# NOTIFICATIONS
# ==========================================

@login_required
def notifications(request):

    notes = request.user.notifications.select_related("sender", "post").all()

    request.user.notifications.filter(is_read=False).update(is_read=True)

    paginator = Paginator(notes, 20)
    notes = paginator.get_page(request.GET.get("page"))

    return render(request, "notifications.html", {"notifications": notes})
