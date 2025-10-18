from django.shortcuts import render

# Create your views here.

def homepage(request):
  return render(request, 'index/homepage.html')
def aboutpage(request):
  return render(request, 'index/aboutpage.html')
def vision_missionpage(request):
  return render(request, 'index/homepage.html')