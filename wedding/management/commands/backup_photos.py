import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from wedding.models import Photo

class Command(BaseCommand):
    help = 'Backup all wedding photos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--destination',
            type=str,
            help='Destination directory for backup',
            default=f'backup_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        )

    def handle(self, *args, **options):
        destination = options['destination']
        
        # Create backup directory
        if not os.path.exists(destination):
            os.makedirs(destination)
            self.stdout.write(f'Created backup directory: {destination}')

        photos = Photo.objects.all()
        copied_count = 0
        error_count = 0

        for photo in photos:
            if photo.image and os.path.exists(photo.image.path):
                try:
                    # Create subdirectory by upload date
                    date_dir = photo.upload_date.strftime('%Y-%m')
                    dest_dir = os.path.join(destination, date_dir)
                    
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    
                    # Copy file
                    filename = os.path.basename(photo.image.path)
                    dest_path = os.path.join(dest_dir, f"{photo.id}_{filename}")
                    
                    shutil.copy2(photo.image.path, dest_path)
                    copied_count += 1
                    
                    # Create info file
                    info_path = os.path.join(dest_dir, f"{photo.id}_{filename}.txt")
                    with open(info_path, 'w', encoding='utf-8') as f:
                        f.write(f"Title: {photo.title}\n")
                        f.write(f"Description: {photo.description}\n")
                        f.write(f"Category: {photo.get_category_display()}\n")
                        f.write(f"Uploaded by: {photo.uploaded_by.get_full_name()}\n")
                        f.write(f"Upload date: {photo.upload_date}\n")
                        f.write(f"Approved: {photo.approved}\n")
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error copying {photo.title}: {e}')
                    )
                    error_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'File not found for photo: {photo.title}')
                )
                error_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Backup completed!\n'
                f'Copied: {copied_count} files\n'
                f'Errors: {error_count}\n'
                f'Destination: {destination}'
            )
        )