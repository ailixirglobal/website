from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseServerError, HttpResponseNotFound
from django.views.decorators.csrf import requires_csrf_token
from django.template import TemplateDoesNotExist
import uuid
import logging
from django.core.mail import send_mail
from django.contrib import messages
from .utils.herbal_analyzer import analyze_herbal_symptoms
from .models import SocialHandle, Product
# Create your views here.

def homepage(request):
  context = {}
  products = Product.objects.all()
  context['products'] = products
  return render(request, 'index/homepage.html', context)

def contact_us(request):
  if request.method == 'POST':
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    subject = request.POST.get('subject')
    message = request.POST.get('message')
    our_message = f'''
Dear {name}, We are glad that you reach to us, we will reply you as soon as possible thank you so much.
    
we received the following mail:
———————————
Subject : {subject}

message : 
{message}
___________
we can reach out to you through your provided phone number {phone}
we all from Ailixir Global Limited, we say THANK YOU!
    '''
    send_mail('Thank you for contacting us.', our_message, 'info@ailixirglobal.com', [email])
    messages.add_message(request, messages.INFO,'Thank You for contacting Us.')
  return redirect('home')
  
def aboutpage(request):
  return render(request, 'index/aboutpage.html')

def contactpage(request):
  return render(request, 'index/contactpage.html')

def vision_missionpage(request):
  return render(request, 'index/homepage.html')



def herbal_recommendation_api(request):
    """
    API endpoint for herbal recommendations.
    Example: /api/herbal?symptoms=fever, headache
    """
    symptoms = request.GET.get("symptoms", "")
    results = analyze_herbal_symptoms(symptoms)
    return JsonResponse({"symptoms": symptoms, "results": results})
  
  

logger = logging.getLogger(__name__)

def get_error_context(request):
    """Get common context for error pages"""
    return {
        'request': request,
        'user': getattr(request, 'user', None),
    }

@requires_csrf_token
def custom_404_view(request, exception=None):
    """
    Custom 404 error handler
    """
    try:
        context = get_error_context(request)
        context.update({
            'exception': str(exception) if exception else None,
            'path': request.path,
        })
        
        # Log the 404 error
        logger.warning(f"404 - Page not found: {request.path}", extra={
            'status_code': 404,
            'request': request,
        })
        
        return render(request, 'index/404.html', context, status=404)
        
    except TemplateDoesNotExist:
        # Fallback if template doesn't exist
        return HttpResponseNotFound('<h1>Page not found</h1><p>The requested page does not exist.</p>')

@requires_csrf_token
def custom_500_view(request):
    """
    Custom 500 error handler
    """
    try:
        # Generate unique error ID for tracking
        error_id = str(uuid.uuid4())[:8]
        
        context = get_error_context(request)
        context.update({
            'error_id': error_id,
        })
        
        # Log the 500 error
        logger.error(f"500 - Server error", extra={
            'status_code': 500,
            'request': request,
            'error_id': error_id,
        })
        
        return render(request, 'index/500.html', context, status=500)
        
    except TemplateDoesNotExist:
        # Fallback if template doesn't exist
        return HttpResponseServerError('<h1>Server Error</h1><p>An internal server error occurred.</p>')
  
  