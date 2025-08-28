from django.core.management.base import BaseCommand
from wedding.models import Photo
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Zarządza zdjęciami weselnych - masowe zatwierdzanie, usuwanie itp.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--approve-all',
            action='store_true',
            help='Zatwierdza wszystkie oczekujące zdjęcia',
        )
        parser.add_argument(
            '--approve-by-uploader',
            type=str,
            help='Zatwierdza wszystkie zdjęcia od konkretnej osoby',
        )
        parser.add_argument(
            '--approve-recent',
            type=int,
            help='Zatwierdza zdjęcia z ostatnich X godzin',
        )
        parser.add_argument(
            '--show-pending',
            action='store_true',
            help='Pokaż oczekujące zdjęcia',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Pokaż statystyki zdjęć',
        )
        parser.add_argument(
            '--feature-best',
            type=int,
            help='Automatycznie wyróżnij X najnowszych zdjęć',
        )

    def handle(self, *args, **options):
        if options['stats']:
            self.show_stats()
        elif options['show_pending']:
            self.show_pending_photos()
        elif options['approve_all']:
            self.approve_all_photos()
        elif options['approve_by_uploader']:
            self.approve_by_uploader(options['approve_by_uploader'])
        elif options['approve_recent']:
            self.approve_recent_photos(options['approve_recent'])
        elif options['feature_best']:
            self.feature_best_photos(options['feature_best'])
        else:
            self.show_help()

    def show_stats(self):
        """Pokazuje statystyki zdjęć"""
        total = Photo.objects.count()
        approved = Photo.objects.filter(approved=True).count()
        pending = Photo.objects.filter(approved=False).count()
        featured = Photo.objects.filter(featured=True).count()
        
        self.stdout.write(self.style.SUCCESS('📊 STATYSTYKI ZDJĘĆ'))
        self.stdout.write('='*30)
        self.stdout.write(f'📸 Wszystkich zdjęć: {total}')
        self.stdout.write(f'✅ Zatwierdzonych: {approved}')
        self.stdout.write(f'⏳ Oczekujących: {pending}')
        self.stdout.write(f'⭐ Wyróżnionych: {featured}')
        
        if total > 0:
            approval_rate = (approved / total) * 100
            self.stdout.write(f'📈 Wskaźnik zatwierdzenia: {approval_rate:.1f}%')
        
        # Statystyki przesyłających
        uploaders = Photo.objects.exclude(uploader_name='').values_list('uploader_name', flat=True).distinct()
        if uploaders:
            self.stdout.write('\n👥 TOP PRZESYŁAJĄCY:')
            for uploader in uploaders[:5]:
                count = Photo.objects.filter(uploader_name=uploader).count()
                approved_count = Photo.objects.filter(uploader_name=uploader, approved=True).count()
                self.stdout.write(f'   {uploader}: {approved_count}/{count} zdjęć')

    def show_pending_photos(self):
        """Pokazuje oczekujące zdjęcia"""
        pending = Photo.objects.filter(approved=False).order_by('-upload_date')
        
        if not pending.exists():
            self.stdout.write(self.style.SUCCESS('✅ Brak oczekujących zdjęć!'))
            return
        
        self.stdout.write(f'⏳ OCZEKUJĄCE ZDJĘCIA ({pending.count()})')
        self.stdout.write('='*50)
        
        for photo in pending[:10]:  # Pokaż pierwsze 10
            uploader = photo.uploader_display_name
            time_ago = timezone.now() - photo.upload_date
            hours = int(time_ago.total_seconds() / 3600)
            
            self.stdout.write(f'📷 {photo.title[:30]}...')
            self.stdout.write(f'   👤 {uploader}')
            self.stdout.write(f'   ⏰ {hours}h temu')
            self.stdout.write(f'   🏷️  {photo.get_category_display()}')
            self.stdout.write('')
        
        if pending.count() > 10:
            self.stdout.write(f'... i {pending.count() - 10} więcej')

    def approve_all_photos(self):
        """Zatwierdza wszystkie oczekujące zdjęcia"""
        pending = Photo.objects.filter(approved=False)
        count = pending.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ Brak zdjęć do zatwierdzenia!'))
            return
        
        confirm = input(f'❓ Zatwierdzić wszystkie {count} oczekujących zdjęć? [y/N]: ')
        if confirm.lower() in ['y', 'yes', 'tak', 't']:
            pending.update(approved=True)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Zatwierdzono {count} zdjęć!')
            )
        else:
            self.stdout.write('❌ Anulowano')

    def approve_by_uploader(self, uploader_name):
        """Zatwierdza wszystkie zdjęcia od konkretnej osoby"""
        photos = Photo.objects.filter(
            uploader_name__icontains=uploader_name,
            approved=False
        )
        count = photos.count()
        
        if count == 0:
            self.stdout.write(f'❌ Brak oczekujących zdjęć od "{uploader_name}"')
            return
        
        self.stdout.write(f'📸 Znaleziono {count} oczekujących zdjęć od "{uploader_name}":')
        for photo in photos[:5]:  # Pokaż przykłady
            self.stdout.write(f'   • {photo.title}')
        if count > 5:
            self.stdout.write(f'   ... i {count - 5} więcej')
        
        confirm = input(f'\n❓ Zatwierdzić wszystkie? [y/N]: ')
        if confirm.lower() in ['y', 'yes', 'tak', 't']:
            photos.update(approved=True)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Zatwierdzono {count} zdjęć od "{uploader_name}"!')
            )
        else:
            self.stdout.write('❌ Anulowano')

    def approve_recent_photos(self, hours):
        """Zatwierdza zdjęcia z ostatnich X godzin"""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        photos = Photo.objects.filter(
            upload_date__gte=cutoff_time,
            approved=False
        )
        count = photos.count()
        
        if count == 0:
            self.stdout.write(f'❌ Brak oczekujących zdjęć z ostatnich {hours} godzin')
            return
        
        self.stdout.write(f'📸 Znaleziono {count} oczekujących zdjęć z ostatnich {hours} godzin')
        
        # Grupuj po przesyłających
        uploaders = {}
        for photo in photos:
            uploader = photo.uploader_display_name
            if uploader not in uploaders:
                uploaders[uploader] = []
            uploaders[uploader].append(photo)
        
        for uploader, uploader_photos in uploaders.items():
            self.stdout.write(f'   👤 {uploader}: {len(uploader_photos)} zdjęć')
        
        confirm = input(f'\n❓ Zatwierdzić wszystkie {count} zdjęć? [y/N]: ')
        if confirm.lower() in ['y', 'yes', 'tak', 't']:
            photos.update(approved=True)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Zatwierdzono {count} zdjęć z ostatnich {hours} godzin!')
            )
        else:
            self.stdout.write('❌ Anulowano')

    def feature_best_photos(self, count):
        """Automatycznie wyróżnia najlepsze zdjęcia"""
        # Wybierz najnowsze zatwierdzone zdjęcia
        photos = Photo.objects.filter(approved=True, featured=False).order_by('-upload_date')[:count]
        
        if not photos.exists():
            self.stdout.write('❌ Brak zdjęć do wyróżnienia')
            return
        
        actual_count = len(photos)
        self.stdout.write(f'⭐ Wybrano {actual_count} najnowszych zdjęć do wyróżnienia:')
        
        for photo in photos:
            self.stdout.write(f'   📷 {photo.title} - {photo.uploader_display_name}')
        
        confirm = input(f'\n❓ Wyróżnić te {actual_count} zdjęć? [y/N]: ')
        if confirm.lower() in ['y', 'yes', 'tak', 't']:
            for photo in photos:
                photo.featured = True
                photo.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'⭐ Wyróżniono {actual_count} zdjęć!')
            )
        else:
            self.stdout.write('❌ Anulowano')

    def show_help(self):
        """Pokazuje pomoc"""
        self.stdout.write(self.style.SUCCESS('📸 Manager Zdjęć Weselnych'))
        self.stdout.write('')
        self.stdout.write('Dostępne opcje:')
        self.stdout.write('  --stats                     Pokaż statystyki zdjęć')
        self.stdout.write('  --show-pending             Pokaż oczekujące zdjęcia')
        self.stdout.write('  --approve-all              Zatwierdź wszystkie oczekujące')
        self.stdout.write('  --approve-by-uploader NAME Zatwierdź od konkretnej osoby')
        self.stdout.write('  --approve-recent HOURS     Zatwierdź z ostatnich X godzin')
        self.stdout.write('  --feature-best N           Wyróżnij N najnowszych zdjęć')
        self.stdout.write('')
        self.stdout.write('Przykłady:')
        self.stdout.write('  python manage.py manage_photos --stats')
        self.stdout.write('  python manage.py manage_photos --approve-all')
        self.stdout.write('  python manage.py manage_photos --approve-by-uploader "Anna"')
        self.stdout.write('  python manage.py manage_photos --approve-recent 2')
        self.stdout.write('  python manage.py manage_photos --feature-best 5')