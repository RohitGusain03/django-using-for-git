from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from blog.models import Post, Notification
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Follow


@login_required
def profile(request):
    return redirect("public_profile", username=request.user.username)


def public_profile(request, username):

    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile

    tab = request.GET.get("tab", "posts")

    if tab == "saved" and request.user == profile_user:
        posts = profile_user.saved_posts.all().order_by("-created_at")
    elif tab == "liked" and request.user == profile_user:
        posts = profile_user.liked_posts.all().order_by("-created_at")
    else:
        tab = "posts"
        posts = profile_user.posts.all().order_by("-created_at")

    posts = posts.select_related("author", "author__profile", "category").prefetch_related(
        "tags", "likes", "saved_by", "media"
    )

    paginator = Paginator(posts, 9)
    posts = paginator.get_page(request.GET.get("page"))

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, following=profile_user
        ).exists()

    return render(
        request,
        "profile.html",
        {
            "profile_user": profile_user,
            "profile": profile,
            "posts": posts,
            "tab": tab,
            "is_own_profile": request.user == profile_user,
            "is_following": is_following,
        },
    )


@login_required
def edit_profile(request):

    profile = request.user.profile

    if request.method == "POST":

        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()
            profile_form.save()

            messages.success(request, "Profile updated successfully.")

            return redirect("public_profile", username=request.user.username)

    else:

        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(
        request,
        "edit_profile.html",
        {"user_form": user_form, "form": profile_form},
    )


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect("login")

    else:

        form = RegisterForm()

    return render(request, "register.html", {"form": form})


@login_required
def toggle_follow(request, username):

    target = get_object_or_404(User, username=username)

    if target != request.user:

        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=target
        )

        if created:
            following = True
            Notification.objects.create(
                recipient=target,
                sender=request.user,
                notification_type=Notification.FOLLOW,
            )
        else:
            follow.delete()
            following = False
    else:
        following = False

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {"following": following, "follower_count": target.profile.follower_count}
        )

    return redirect("public_profile", username=username)


def follow_list(request, username, kind):

    profile_user = get_object_or_404(User, username=username)

    if kind == "followers":
        users = User.objects.filter(following__following=profile_user)
        title = "Followers"
    else:
        users = User.objects.filter(followers__follower=profile_user)
        title = "Following"

    return render(
        request,
        "follow_list.html",
        {"profile_user": profile_user, "users": users, "title": title},
    )
