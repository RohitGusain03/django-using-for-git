from django.urls import path
from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path("post/<int:post_id>/", views.post_details, name="post_detail"),

    path("comment/delete/<int:comment_id>/", views.delete_comment, name="delete_comment"),

    path("create/", views.create_post, name="create_post"),

    path("edit/<int:post_id>/", views.edit_post, name="edit_post"),

    path("comment/<int:comment_id>/edit/", views.edit_comment, name="edit_comment"),

    path("comment/<int:comment_id>/like/", views.like_comment, name="like_comment"),

    path("post/<int:post_id>/save/", views.save_post, name="save_post"),

    path("saved_posts/", views.saved_posts, name="saved_posts"),

    path("delete/<int:post_id>/", views.delete_post, name="delete_post"),

    path("category/<int:category_id>/", views.category_posts, name="category_posts"),

    path("tag/<slug:slug>/", views.tag_posts, name="tag_posts"),

    path("post/<int:post_id>/like/", views.like_post, name="like_post"),

    path("post-media/<int:media_id>/delete/", views.delete_post_media, name="delete_post_media"),

    path("notifications/", views.notifications, name="notifications"),
]
