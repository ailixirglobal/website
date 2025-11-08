from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .models import Subscriber
# Create your views here.

def subscribe(request):
  if request.method == "POST":
    email = request.POST.get('email', None)
    if email == None:
      return redirect('home')
    if Subscriber.objects.filter(email=email).exists():
      messages.add_message(request, messages.SUCCESS, "You are already subscribed.")
      return redirect('home')
    Subscriber.objects.create(email=email)
    message = 'Thank you for Subscribing, we will keep you upto date.'
    send_mail('Subscription to Ailixir News Letter', message, 'Ailixir Global Limited NewsLetter <info@ailixirglobal.com>', [email])
    messages.add_message(request, messages.SUCCESS, "Thanks for subscribing.")
  return redirect('home')