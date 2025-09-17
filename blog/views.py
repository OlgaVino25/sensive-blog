from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Count, Prefetch


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        "first_tag_title": post.tags.all()[0].title,
    }


def serialize_post_optimized(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        "first_tag_title": post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        "title": tag.title,
        "posts_with_tag": (tag.posts_count if hasattr(tag, "posts_count") else 0),
    }


def index(request):
    most_popular_posts = (
        Post.objects.popular().fully_optimized()[:5].fetch_with_comments_count()
    )

    most_fresh_posts = (
        Post.objects.order_by("-published_at")
        .fully_optimized()[:5]
        .fetch_with_comments_count()
    )

    fresh_posts_ids = [post.id for post in most_fresh_posts]
    fresh_posts_with_likes = Post.objects.filter(id__in=fresh_posts_ids).annotate(
        likes_count=Count("likes", distinct=True)
    )
    likes_for_id = {post.id: post.likes_count for post in fresh_posts_with_likes}

    for post in most_fresh_posts:
        post.likes_count = likes_for_id.get(post.id, 0)

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        "most_popular_posts": [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
        "page_posts": [serialize_post_optimized(post) for post in most_fresh_posts],
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    post = (
        Post.objects.select_related("author")
        .prefetch_related(
            "comments__author",
            Prefetch("tags", queryset=Tag.objects.annotate(posts_count=Count("posts"))),
        )
        .annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )
        .get(slug=slug)
    )

    serialized_comments = []
    for comment in post.comments.all():
        serialized_comments.append(
            {
                "text": comment.text,
                "published_at": comment.published_at,
                "author": comment.author.username,
            }
        )

    serialized_tags = [serialize_tag(tag) for tag in post.tags.all()]

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        "likes_amount": post.likes_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": serialized_tags,
    }

    most_popular_posts = (
        Post.objects.popular().fully_optimized()[:5].fetch_with_comments_count()
    )

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        "post": serialized_post,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "most_popular_posts": [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_posts = (
        Post.objects.popular().fully_optimized()[:5].fetch_with_comments_count()
    )

    most_popular_tags = Tag.objects.popular()[:5]

    related_posts = (
        Post.objects.filter(tags=tag).fully_optimized()[:20].fetch_with_comments_count()
    )

    related_posts_ids = [post.id for post in related_posts]

    related_posts_with_likes = Post.objects.filter(id__in=related_posts_ids).annotate(
        likes_count=Count("likes", distinct=True)
    )

    likes_for_id = {post.id: post.likes_count for post in related_posts_with_likes}

    for post in related_posts:
        post.likes_count = likes_for_id.get(post.id, 0)

    context = {
        "tag": tag.title,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post_optimized(post) for post in related_posts],
        "most_popular_posts": [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, "posts-list.html", context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, "contacts.html", {})
