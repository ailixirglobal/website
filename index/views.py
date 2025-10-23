from django.shortcuts import render
from .models import SocialHandle
# Create your views here.

def homepage(request):
  context = {}
  handles = SocialHandle.objects.all()
  context['handles'] = handles
  return render(request, 'index/homepage.html', context)
def aboutpage(request):
  return render(request, 'index/aboutpage.html')
def contactpage(request):
  return render(request, 'index/contactpage.html')
def vision_missionpage(request):
  return render(request, 'index/homepage.html')