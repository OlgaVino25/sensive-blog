from django.shortcuts import render, get_object_or_404
from blog.models import Post, Tag
from django.db.models import Count, Prefetch


def serialize_post_optimized(post):
    post_tags = post.tags.all()
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag_optimized(tag) for tag in post_tags],
        "first_tag_title": post_tags[0].title if post_tags else None,
    }


def serialize_tag_optimized(tag):
    return {
        "title": tag.title,
        "posts_with_tag": tag.posts_count,
    }


def index(request):
    most_popular_posts = Post.objects.popular()[:5].fully_optimized()

    most_fresh_posts = Post.objects.order_by("-published_at")[:5].fully_optimized()

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
        "popular_tags": [serialize_tag_optimized(tag) for tag in most_popular_tags],
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related("author")
        .prefetch_related("comments__author")
        .with_prefetched_tags()
        .annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        ),
        slug=slug,
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

    serialized_tags = [serialize_tag_optimized(tag) for tag in post.tags.all()]

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

    most_popular_posts = Post.objects.popular()[:5].fully_optimized()

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        "post": serialized_post,
        "popular_tags": [serialize_tag_optimized(tag) for tag in most_popular_tags],
        "most_popular_posts": [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)

    most_popular_posts = Post.objects.popular()[:5].fully_optimized()

    most_popular_tags = Tag.objects.popular()[:5]

    related_posts = Post.objects.filter(tags=tag)[:20].fully_optimized()

    related_posts_ids = [post.id for post in related_posts]
    related_posts_with_likes = Post.objects.filter(id__in=related_posts_ids).annotate(
        likes_count=Count("likes", distinct=True)
    )
    likes_for_id = {post.id: post.likes_count for post in related_posts_with_likes}

    for post in related_posts:
        post.likes_count = likes_for_id.get(post.id, 0)

    context = {
        "tag": tag.title,
        "popular_tags": [serialize_tag_optimized(tag) for tag in most_popular_tags],
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
