from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    path("register/", views.register, name="register"),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("profile/", views.profile, name="profile"),

    path("profile/edit/", views.edit_profile, name="edit_profile"),

    path("u/<str:username>/", views.public_profile, name="public_profile"),

    path("u/<str:username>/follow/", views.toggle_follow, name="toggle_follow"),

    path("u/<str:username>/<str:kind>/", views.follow_list, name="follow_list"),
]
