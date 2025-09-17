from django.contrib import admin
from blog.models import Post, Tag, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at")
    list_select_related = ("author",)
    raw_id_fields = ("author", "tags", "likes")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "published_at")
    list_select_related = ("post", "author")
    raw_id_fields = ("post", "author")
    list_filter = ("published_at",)
    search_fields = ("text", "post__title")


class TagAdmin(admin.ModelAdmin):
    list_display = ("title", "posts_count")
    search_fields = ("title",)

    def posts_count(self, obj):
        return obj.posts.count()

    posts_count.short_description = "Количество постов"


admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment, CommentAdmin)
