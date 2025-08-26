from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Photo, Guest

@receiver(post_save, sender=Photo)
def photo_uploaded_notification(sender, instance, created, **kwargs):
    """Send notification when new photo is uploaded"""
    if created and not instance.approved:
        # Notify admin about new photo for moderation
        subject = f"Nowe zdjęcie czeka na zatwierdzenie - {instance.title}"
        message = f"""
        Nowe zdjęcie zostało przesłane przez {instance.uploaded_by.get_full_name()}:
        
        Tytuł: {instance.title}
        Kategoria: {instance.get_category_display()}
        Opis: {instance.description or 'Brak opisu'}
        
        Przejdź do panelu administracyjnego aby zatwierdzić.
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except:
            pass  # Ignore email errors in development

@receiver(post_save, sender=User)
def create_guest_profile(sender, instance, created, **kwargs):
    """Automatically create Guest profile when User is created"""
    if created:
        Guest.objects.get_or_create(user=instance)