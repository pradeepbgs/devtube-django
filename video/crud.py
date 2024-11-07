from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from .models import  VideoModel 
from comment.models import CommentModel
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models import Q,Count,BooleanField,Case,When,Value,F
User = get_user_model()

@sync_to_async
def fetch_user_by_userId(userId):
    try:
        return get_object_or_404(User,id=userId)
    except:
        return None

@sync_to_async
def get_videos(filters,order_by):
    return list(VideoModel.objects.filter(filters).order_by(order_by))

@sync_to_async
def fetch_user_videos(user):
    return list(VideoModel.objects.filter(owner=user).order_by('created_at'))

@sync_to_async
def get_paginated_videos(videos, limit, page):
    try:
        paginator = Paginator(videos, limit)
        paginated_videos = paginator.get_page(page)
    except (EmptyPage, PageNotAnInteger):
        paginated_videos = paginator.page(1)
    return {
        'pagination_data': paginated_videos,
        'total': paginator.count,
        'total_pages': paginator.num_pages
    }

@sync_to_async
def save_video(title, description, thumbnail, video_file, duration, owner):
    return VideoModel.objects.create(
        title=title,
        description=description,
        thumbnail=thumbnail,
        video_file=video_file,
        duration=duration,
        owner=owner
    )


@sync_to_async
def fetch_video_details(video, user):
    return VideoModel.objects.filter(id=video.id).annotate(
            like_count=Count('likes', filter=Q(likes__video=video)),
            subscribers_count=Count('owner__subscribers', filter=Q(owner__subscribers__channel=F('owner'))),
            is_liked=Case(
                When(likes__liked_by=user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ) if user else Value(False, output_field=BooleanField()),
                is_subscribed=Case(
                    When(owner__subscriptions__subscriber=user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ) if user else Value(False, output_field=BooleanField())
            ).values(
                'id', 'title', 'description', 'thumbnail', 'video_file', 'views', 'isPublished', 'duration',
                'created_at', 'updated_at',
                'like_count', 'subscribers_count', 'is_liked', 'is_subscribed',
                'owner__id',
                'owner__fullname',
                'owner__username',
                'owner__avatar',
            ).first()

@sync_to_async
def get_video_comments(video):
    return CommentModel.objects.filter(video=video).order_by('created_at')

@sync_to_async
def get_paginated_comments(comments, limit, page):
    paginator = Paginator(comments, limit)
    try:
        paginated_comments = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        paginated_comments = paginator.page(1)
    return paginated_comments