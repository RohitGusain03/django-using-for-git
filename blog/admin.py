from django.contrib import admin
from .models import Post, Category, Comment, Tag, PostMedia, Notification


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ("id", "name", "icon")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ("id", "name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = ("id", "title", "author", "category", "views", "created_at")

    search_fields = ("title", "content")

    list_filter = ("category", "tags", "created_at")

    filter_horizontal = ("tags",)

    inlines = [PostMediaInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = ("author", "post", "parent", "created_at")

    search_fields = ("author__username", "post__title", "content")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = ("recipient", "sender", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
