from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from blog.models import Post

@login_required
def profile(request):
    user = request.user
    total_posts = user.post_set.count()
    context = {
        "user": user,
        "total_posts": total_posts,
    }
    return render(request, "profile.html", context)

def register(request):

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = RegisterForm()

    return render(
        request,
        "register.html",
        {
            "form": form
         }
    )

