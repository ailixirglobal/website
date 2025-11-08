from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from .models import Post
from newsletter.models import Subscriber

@receiver(post_save, sender=Post)
def send_blog_notification(sender, instance, created, **kwargs):
    # Only send if a new post is created AND published
    if created and instance.is_published:
        subscribers = Subscriber.objects.all()
        if not subscribers:
            return

        subject = f"New Post: {instance.title}"
        from_email = settings.DEFAULT_FROM_EMAIL

        # Build absolute URL for the post
        domain = getattr(settings, 'SITE_DOMAIN', 'ailixirglobal.com')
        post_url = instance.get_absolute_url()

        html_message = render_to_string('emails/email.html', {
            'title': instance.title,
            'excerpt': instance.excerpt,
            'url': post_url,
            'image': instance.featured_image.url if instance.featured_image else None,
        })
        plain_message = strip_tags(html_message)

        messages = [
            (subject, html_message, from_email, [subscriber.email])
            for subscriber in subscribers
        ]

        send_mass_mail(messages, fail_silently=False)