from django.urls import path
from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path(
        "post/<int:post_id>/",
        views.post_details,
        name="post_detail"
    ),

    path(
        "comment/delete/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment"
    ),

    path(
        "create/",
        views.create_post,
        name="create_post"
    ),

    path(
        "edit/<int:post_id>/",
        views.edit_post,
        name="edit_post"
    ),

    path(
        "delete/<int:post_id>/",
        views.delete_post,
        name="delete_post"
    ),

    path(
        "category/<int:category_id>/",
        views.category_posts,
        name="category_posts"
    ),

]