from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .serializers import PostSerializer, PostCreateSerializer, CategorySerializer, TagSerializer, CommentSerializer
from blog.models import Post, Category, Tag, Comment

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostListCreateAPIView(generics.ListCreateAPIView):
    """
    List all posts or create a new post.
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-created_at')
        
        # Filter by status (published only for non-staff users)
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='published')
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()
        
        # Filter by category
        category_id = self.request.query_params.get('category', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by tag
        tag_id = self.request.query_params.get('tag', None)
        if tag_id is not None:
            queryset = queryset.filter(tags__id=tag_id)
        
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a post instance.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Only author or staff can edit/delete
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def check_object_permissions(self, request, obj):
        # Allow everyone to read, but only author or staff to edit/delete
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.author != request.user and not request.user.is_staff:
                self.permission_denied(
                    request,
                    message='You do not have permission to perform this action.',
                    code='permission_denied'
                )
        super().check_object_permissions(request, obj)

    def retrieve(self, request, *args, **kwargs):
        # Increment view count
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        return super().retrieve(request, *args, **kwargs)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post_api(request):
    """
    API endpoint for creating a post.
    """
    serializer = PostCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        post = serializer.save()
        response_serializer = PostSerializer(post, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_posts_api(request):
    """
    API endpoint for getting posts with filtering and pagination.
    """
    posts = Post.objects.filter(status='published').order_by('-created_at')
    
    # Apply filters
    category_id = request.query_params.get('category', None)
    if category_id:
        posts = posts.filter(category_id=category_id)
    
    tag_id = request.query_params.get('tag', None)
    if tag_id:
        posts = posts.filter(tags__id=tag_id)
    
    search = request.query_params.get('search', None)
    if search:
        posts = posts.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search) |
            Q(tags__name__icontains=search)
        ).distinct()
    
    # Pagination
    paginator = StandardResultsSetPagination()
    paginated_posts = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def get_categories_api(request):
    """
    API endpoint for getting all categories.
    """
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_tags_api(request):
    """
    API endpoint for getting all tags.
    """
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)

class CommentListCreateAPIView(generics.ListCreateAPIView):
    """
    List all comments for a post or create a new comment.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_slug = self.kwargs['post_slug']
        post = get_object_or_404(Post, slug=post_slug)
        return Comment.objects.filter(post=post, is_approved=True).order_by('-created_at')

    def perform_create(self, serializer):
        post_slug = self.kwargs['post_slug']
        post = get_object_or_404(Post, slug=post_slug)
        serializer.save(author=self.request.user, post=post)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment_api(request, post_slug):
    """
    API endpoint for adding a comment to a post.
    """
    post = get_object_or_404(Post, slug=post_slug)
    serializer = CommentSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        comment = serializer.save(author=request.user, post=post)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)