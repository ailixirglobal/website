from django.urls import path
from index.views import homepage, aboutpage, contactpage

urlpatterns = [
    path('', homepage, name='home'),
    path('about-us/', aboutpage, name='about'),
    path('contact-us/', contactpage, name='contact'),
]
