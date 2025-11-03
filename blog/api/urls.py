from django.urls import path
from . import views

urlpatterns = [
    # Post endpoints
    path('posts/', views.PostListCreateAPIView.as_view(), name='api-post-list-create'),
    path('posts/create/', views.create_post_api, name='api-post-create'),
    path('posts/list/', views.get_posts_api, name='api-posts-list'),
    path('posts/<slug:slug>/', views.PostDetailAPIView.as_view(), name='api-post-detail'),
    
    # Category and Tag endpoints
    path('categories/', views.get_categories_api, name='api-categories-list'),
    path('tags/', views.get_tags_api, name='api-tags-list'),
    
    # Comment endpoints
    path('posts/<slug:post_slug>/comments/', views.CommentListCreateAPIView.as_view(), name='api-comment-list-create'),
    path('posts/<slug:post_slug>/comments/add/', views.add_comment_api, name='api-add-comment'),
]