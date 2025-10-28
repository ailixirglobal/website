from index.models import SocialHandle


def global_variables(request):
    context = {}
    handles = SocialHandle.objects.all()
    context['handles'] = handles
    return context