from django.urls import path, include
from . import views

app_name = 'blog'

urlpatterns = [
    # Main blog pages
    path('', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    
    # Post CRUD operations
    path('create/', views.post_create, name='post_create'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/update/', views.post_update, name='post_update'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    
    # Comments
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    
    # Categories and tags
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
    path('tag/<slug:tag_slug>/', views.tag_posts, name='tag_posts'),
    
    # Search
    path('search/', views.search_posts, name='search_posts'),
    
    path('api/', include('blog.api.urls'))
]