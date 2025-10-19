from django.shortcuts import render, redirect
from django.core.mail import send_mail
# Create your views here.

def subscribe(request):
  if request.method == "POST":
    email = request.POST.get('email', None)
    if email == None:
      return redirect('home')
    message = 'Thank you for Subscribing, we will keep you upto date.'
    send_mail('Subscription to Ailixir News Letter', message, 'info@ailixirglobal.com', [email])
  return redirect('home')