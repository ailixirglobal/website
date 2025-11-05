from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Post, Category, Tag, Comment
from .forms import PostForm, CommentForm

import os, json
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from .models import Attachment

@require_POST
def summernote_upload(request):
    """Handles Summernote image upload."""
    files = request.FILES.getlist('file') or request.FILES.getlist('files[]') or []
    if not files:
        return HttpResponseBadRequest('No files received')

    uploaded = []
    for f in files:
        attach = Attachment.objects.create(
            uploader=request.user if request.user.is_authenticated else None,
            file=f,
            in_use=False
        )
        uploaded.append({
            'id': attach.id,
            'url': settings.MEDIA_URL + attach.file.name
        })

    return JsonResponse({'attachments': uploaded})

@require_POST
def summernote_delete(request):
    """Handles delete request when image removed from Summernote."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        print(data)
    except Exception as e:
        print(e)
        return HttpResponseBadRequest('Invalid JSON')

    attach_id = data.get('id')
    if not attach_id:
        return HttpResponseBadRequest('Missing id')

    try:
        attach = Attachment.objects.get(pk=attach_id)
    except Attachment.DoesNotExist:
        return JsonResponse({'deleted': False, 'reason': 'not found'})

    # Remove the file from storage
    if default_storage.exists(attach.file.name):
        default_storage.delete(attach.file.name)
    attach.delete()

    return JsonResponse({'deleted': True})

def post_list(request):
    """Display list of blog posts"""
    posts = Post.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Pagination
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
    }
    
    if request.htmx:
        return render(request, 'blog/post_list.html', context)
    return render(request, 'blog/post_list.html', context)

def post_detail(request, slug):
    """Display individual blog post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Increment view count
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    context = {
        'post': post,
    }
    
    if request.htmx:
        return render(request, 'blog/post_detail.html', context)
    return render(request, 'blog/post_detail.html', context)

@login_required
def post_create(request):
    """Create new blog post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Save many-to-many relationships
            
            messages.success(request, 'Post created successfully!')
            
            if request.htmx:
                return render(request, 'blog/post_detail.html', {'post': post})
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    
    context = {
        'form': form,
    }
    
    if request.htmx:
        return render(request, 'blog/post_form.html', context)
    return render(request, 'blog/post_form.html', context)

@login_required
def post_edit(request, slug):
    """Edit existing blog post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user is the author
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('blog:post_detail', slug=slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request, 'Post updated successfully!')
            
            if request.htmx:
                return render(request, 'blog/post_detail.html', {'post': post})
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
    }
    
    if request.htmx:
        return render(request, 'blog/post_form.html', context)
    return render(request, 'blog/post_form.html', context)

@login_required
def post_update(request, slug):
    """Update blog post (HTMX endpoint)"""
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user is the author
    if post.author != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            form.save_m2m()
            return render(request, 'blog/post_detail.html', {'post': post})
        else:
            context = {
                'form': form,
                'post': post,
            }
            return render(request, 'blog/post_form.html', context)
    
    return redirect('blog:post_edit', slug=slug)

@login_required
def post_delete(request, slug):
    """Delete blog post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user is the author
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('blog:post_detail', slug=slug)
    
    if request.method == 'DELETE' or request.POST.get('_method') == 'DELETE':
        post_title = post.title
        post.delete()
        messages.success(request, f'Post "{post_title}" deleted successfully!')
        
        # Return the post list after deletion
        posts = Post.objects.all().order_by('-created_at')
        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(1)
        
        context = {
            'posts': page_obj,
        }
        return render(request, 'blog/post_list.html', context)
    
    return redirect('blog:post_detail', slug=slug)

@require_POST
def add_comment(request, slug):
    """Add comment to a blog post"""
    post = get_object_or_404(Post, slug=slug)
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged in to comment'}, status=403)
    
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        
        # Return the new comment HTML
        context = {
            'comment': comment,
        }
        return redirect('blog:post_detail', post.slug)
        return render(request, 'blog/post_detail.html', context)
    
    return JsonResponse({'error': 'Invalid form data'}, status=400)

def category_posts(request, category_slug):
    """Display posts by category"""
    category = get_object_or_404(Category, slug=category_slug)
    posts = Post.objects.filter(category=category, status='published').order_by('-created_at')
    
    context = {
        'posts': posts,
        'category': category,
    }
    
    if request.htmx:
        return render(request, 'blog/post_list.html', context)
    return render(request, 'blog/post_list.html', context)

def tag_posts(request, tag_slug):
    """Display posts by tag"""
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag, status='published').order_by('-created_at')
    
    context = {
        'posts': posts,
        'tag': tag,
    }
    
    if request.htmx:
        return render(request, 'blog/post_list.html', context)
    return render(request, 'blog/post_list.html', context)

def search_posts(request):
    """Search for posts"""
    query = request.GET.get('q', '')
    posts = Post.objects.none()
    
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct().order_by('-created_at')
    
    context = {
        'posts': posts,
        'query': query,
    }
    
    if request.htmx:
        return render(request, 'blog/post_list.html', context)
    return render(request, 'blog/post_list.html', context)
