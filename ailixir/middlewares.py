# middleware.py
from django.contrib.sites.models import Site
from django.conf import settings

class SiteConfigurationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize site on middleware creation
        self.setup_site()
    
    def setup_site(self):
        try:
            site_name = getattr(settings, 'SITE_NAME', 'Ailixir Global Limited')
            site_domain = getattr(settings, 'SITE_DOMAIN', 'ailixirglobal.com')
            
            Site.objects.get_or_create(name=site_name,domain=site_domain)
            
            if not created:
                site.name = site_name
                site.domain = site_domain
                site.save()
                
        except Exception as e:
            # Handle database not ready or other exceptions
            pass
    
    def __call__(self, request):
        response = self.get_response(request)
        return response