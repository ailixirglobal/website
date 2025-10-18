from django.urls import path
from index.views import homepage, aboutpage

urlpatterns = [
    path('', homepage),
    path('about-us/', aboutpage),
]
