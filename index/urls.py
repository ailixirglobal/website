from django.urls import path
from index.views import homepage, aboutpage, contactpage, contact_us
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', homepage, name='home'),
    path('about-us/', aboutpage, name='about'),
    path('contact-us/', contactpage, name='contact'),
    path('contact-us/message/', contact_us, name='contact-us'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)