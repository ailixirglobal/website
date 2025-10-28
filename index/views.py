from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .models import SocialHandle, Product
# Create your views here.

def homepage(request):
  context = {}
  handles = SocialHandle.objects.all()
  products = Product.objects.all()
  context['handles'] = handles
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
  return redirect('home')
  
def aboutpage(request):
  return render(request, 'index/aboutpage.html')

def contactpage(request):
  return render(request, 'index/contactpage.html')

def vision_missionpage(request):
  return render(request, 'index/homepage.html')