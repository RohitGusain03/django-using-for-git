from django.contrib import admin
from .models import Post, Category, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "author",
        "category",
        "created_at",
    )

    search_fields = (
        "title",
        "content",
    )

    list_filter = (
        "category",
        "created_at",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
        "author",
        "post",
        "created_at",
    )

    search_fields = (
        "author__username",
        "post__title",
        "content",
    )