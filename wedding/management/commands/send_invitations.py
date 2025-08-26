from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from wedding.models import Guest, WeddingInfo

class Command(BaseCommand):
    help = 'Send email invitations to all guests'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )

    def handle(self, *args, **options):
        wedding_info = WeddingInfo.objects.first()
        if not wedding_info:
            self.stdout.write(
                self.style.ERROR('No wedding info found. Please create one first.')
            )
            return

        guests = Guest.objects.filter(confirmed=True, user__email__isnull=False).exclude(user__email='')
        
        if not guests.exists():
            self.stdout.write(
                self.style.WARNING('No guests with email addresses found.')
            )
            return

        sent_count = 0
        for guest in guests:
            subject = f"Zaproszenie na wesele {wedding_info.bride_name} & {wedding_info.groom_name}"
            
            # Context for email template
            context = {
                'guest': guest,
                'wedding_info': wedding_info,
                'login_url': 'http://yourdomain.com/',  # Update with your domain
            }
            
            # Render email content
            message = render_to_string('wedding/email/invitation.txt', context)
            html_message = render_to_string('wedding/email/invitation.html', context)
            
            if options['dry_run']:
                self.stdout.write(f"Would send email to: {guest.user.email}")
                self.stdout.write(f"Subject: {subject}")
                self.stdout.write("---")
            else:
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [guest.user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Email sent to {guest.full_name}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to send email to {guest.full_name}: {e}')
                    )

        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent {sent_count} invitations!')
            )