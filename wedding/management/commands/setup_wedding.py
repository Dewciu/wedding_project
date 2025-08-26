from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wedding.models import WeddingInfo, Guest, Table, ScheduleEvent, MenuItem
from datetime import date, time

class Command(BaseCommand):
    help = 'Setup wedding app with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up wedding application...')

        # Create wedding info
        wedding_info, created = WeddingInfo.objects.get_or_create(
            bride_name="Anna",
            groom_name="Marek",
            defaults={
                'wedding_date': date(2024, 6, 15),
                'venue_name': "Pałac Romantyczny",
                'welcome_message': "Cieszymy się, że możecie być z nami w tym wyjątkowym dniu. Ta aplikacja pozwoli Wam dzielić się wspomnieniami, przeglądać zdjęcia i być na bieżąco z harmonogramem uroczystości."
            }
        )
        
        if created:
            self.stdout.write(f'✓ Created wedding info for {wedding_info}')
        else:
            self.stdout.write(f'✓ Wedding info already exists for {wedding_info}')

        # Create tables with realistic layout
        table_data = [
            (1, "Rodzina Panny Młodej", "Najbliższa rodzina ze strony Anny", 10),
            (2, "Rodzina Pana Młodego", "Najbliższa rodzina ze strony Marka", 10),
            (3, "Przyjaciele ze Studiów", "Znajomi z czasów uniwersyteckich", 8),
            (4, "Znajomi z Pracy", "Współpracownicy i koledzy zawodowi", 8),
            (5, "Przyjaciele z Dzieciństwa", "Długoletni przyjaciele", 8),
            (6, "Sąsiedzi i Znajomi", "Przyjaciele z okolicy", 8),
            (7, "Drużbowie i Druhny", "Najbliżsi przyjaciele Pary Młodej", 10),
            (8, "Młodzież", "Młodsza część rodziny i znajomych", 10),
            (9, "Starsze Pokolenie", "Dziadkowie i starsi krewni", 8),
            (10, "Stół Honorowy", "Para Młoda i świadkowie", 6),
        ]

        for number, name, description, capacity in table_data:
            table, created = Table.objects.get_or_create(
                number=number,
                defaults={
                    'name': name,
                    'description': description,
                    'capacity': capacity
                }
            )
            if created:
                self.stdout.write(f'✓ Created table {table}')

        # Create schedule events - zaktualizowany harmonogram
        events_data = [
            ("Przybywanie gości, koktajl powitalny", "Powitanie gości, koktajle i przystawki", time(15, 0), time(15, 30), "Ogród", 1),
            ("Ceremonia ślubna", "Ślub cywilny w ogrodzie", time(15, 30), time(16, 30), "Ogród", 2),
            ("Sesja zdjęciowa i gratulacje", "Zdjęcia z rodziną i przyjaciółmi", time(16, 30), time(17, 45), "Ogród", 3),
            ("Zupa - Krem z pomidorów", "Podanie pierwszego dania", time(17, 45), time(18, 15), "Sala Główna", 4),
            ("Drugie danie - Kotlet schabowy", "Główny obiad weselny, filety z kurczaka dla dzieci", time(18, 15), time(19, 30), "Sala Główna", 5),
            ("Pierwszy taniec Pary Młodej", "", time(19, 30), time(20, 0), "Parkiet", 6),
            ("Rozpoczęcie zabawy tanecznej", "", time(20, 0), time(21, 0), "Parkiet", 7),
            ("Strogonoff", "Hamburgerki dla dzieci", time(21, 0), time(21, 30), "Sala Główna", 8),
            ("Tort weselny i życzenia", "Krojenie tortu weselnego", time(22, 0), time(22, 30), "Sala Główna", 9),
            ("Kontynuacja zabawy", "", time(22, 30), time(23, 30), "Parkiet", 10),
            ("Bitki schabowe z kluskami śląskimi", "Ciepły posiłek w środku nocy", time(23, 30), time(0, 30), "Sala Główna", 11),
            ("Nocna zabawa", "", time(0, 30), time(1, 30), "Parkiet", 12),
            ("Barszczyk czerwony z pasztecikami", "Tradycyjny poranek weselny", time(1, 30), time(2, 30), "Sala Główna", 13),
            ("Zakończenie wesela", "", time(2, 30), time(3, 0), "Sala Główna", 14),
        ]

        for title, description, start_time, end_time, location, order in events_data:
            event, created = ScheduleEvent.objects.get_or_create(
                title=title,
                defaults={
                    'description': description,
                    'start_time': start_time,
                    'end_time': end_time,
                    'location': location,
                    'order': order
                }
            )
            if created:
                self.stdout.write(f'✓ Created event: {event}')

        # Menu items based on wedding schedule
        menu_data = [
            #TODO: Dodac godzine
            # 17:45 - Zupa
            ("Krem z pomidorów z grzanką", "Aromatyczny krem z dojrzałych pomidorów podawany z chrupiącą grzanką", "soup", None, "gluten, mleko", False, 1),
            
            # Drugie danie - Kotlet schabowy
            ("Kotlet schabowy z opiekanymi ziemniaczkami i surówką", "Tradycyjny kotlet schabowy z pieczonymi ziemniakami i mieszanką surówek", "main", None, "gluten, jaja", False, 1),
            
            # Dla dzieci - Filety z kurczaka
            ("Filety z kurczaka z frytkami", "Delikatne filety z kurczaka z chrupiącymi frytkami - specjalnie dla dzieci", "main", None, "", False, 2),
            
            # 21:00 - Strogonoff
            ("Strogonoff", "Klasyczny strogonoff z wołowiną w kremowym sosie z grzybami, podawany z ryżem", "main", None, "mleko", False, 3),
            
            # Dla dzieci - Hamburgerki
            ("Hamburgerki", "Małe hamburgerki z mięsem wołowym i frytkami - dla młodszych gości", "main", None, "gluten", False, 4),
            
            # 22:00 - Tort
            ("Tort weselny", "Wyjątkowy tort weselny - główny deser uroczystości", "dessert", None, "gluten, mleko, jaja", False, 1),
            
            # 23:30 - Bitki schabowe
            ("Bitki schabowe w sosie pieczeniowym z kluskami śląskimi i surówką", "Soczyste bitki schabowe w aromatycznym sosie pieczeniowym z tradycyjnymi kluskami śląskimi", "main", None, "gluten", False, 5),
            
            # 1:30 - Barszczyk czerwony
            ("Barszczyk czerwony z pasztecikami i zapiekankami", "Tradycyjny barszczyk czerwony z domowymi pasztecikami i zapiekankami", "soup", None, "gluten", False, 2),
        ]

        for name, description, course, price, allergens, vegetarian, order in menu_data:
            item, created = MenuItem.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'course': course,
                    'price': price,
                    'allergens': allergens,
                    'vegetarian': vegetarian,
                    'order': order
                }
            )
            if created:
                self.stdout.write(f'✓ Created menu item: {item}')

        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Wedding application setup completed!\n'
                'Utworzono 10 stolików z łączną liczbą ~90 gości\n'
                'Sample login credentials:\n'
                '  Username: jadwiga.kowalska, Password: wesele2024\n'
                '  Username: anna.nowak (Panna Młoda), Password: wesele2024\n'
                '  Username: marek.kowalski (Pan Młody), Password: wesele2024\n'
                '  (i inni...)\n'
            )
        )