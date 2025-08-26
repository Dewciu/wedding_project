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

        # Create tables
        table_data = [
            (1, "Stół Rodziny", "Rodzina Panny Młodej", 8),
            (2, "Stół Przyjaciół", "Przyjaciele ze studiów", 8),
            (3, "Stół Kolegów", "Współpracownicy", 8),
            (4, "Stół VIP", "Najbliżsi znajomi", 6),
            (5, "Stół Młodzieży", "Młodsza część rodziny", 10),
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

        # Create sample guests
        guest_data = [
            ("Jan", "Kowalski", "jan.kowalski", "123456789", 1),
            ("Maria", "Nowak", "maria.nowak", "987654321", 1),
            ("Piotr", "Wiśniewski", "piotr.wisniewski", "555666777", 2),
            ("Katarzyna", "Kowalczyk", "katarzyna.kowalczyk", "444333222", 2),
            ("Tomasz", "Lewandowski", "tomasz.lewandowski", "111222333", 3),
            ("Magdalena", "Dąbrowska", "magdalena.dabrowska", "888999000", 3),
            ("Robert", "Mazur", "robert.mazur", "666777888", 4),
            ("Agnieszka", "Nowak", "agnieszka.nowak", "333444555", 4),
        ]

        for first_name, last_name, username, phone, table_num in guest_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=f"{username}@example.com",
                    password="wesele2024"  # Default password for demo
                )
                guest = Guest.objects.create(
                    user=user,
                    phone_number=phone,
                    table_number=table_num
                )
                self.stdout.write(f'✓ Created guest {guest}')

        # Create schedule events
        events_data = [
            ("Przybywanie gości, koktajl powitalny", "Powitanie gości, koktajle i przystawki", time(15, 0), time(15, 30), "Ogród", 1),
            ("Ceremonia ślubna", "Ślub cywilny w ogrodzie", time(15, 30), time(16, 30), "Ogród", 2),
            ("Sesja zdjęciowa i gratulacje", "Zdjęcia z rodziną i przyjaciółmi", time(16, 30), time(17, 30), "Ogród", 3),
            ("Obiad weselny", "Powitanie w sali, obiad", time(17, 30), time(19, 0), "Sala Główna", 4),
            ("Pierwszy taniec Pary Młodej", "", time(19, 0), time(19, 30), "Parkiet", 5),
            ("Rozpoczęcie zabawy tanecznej", "", time(19, 30), time(22, 0), "Parkiet", 6),
            ("Tort weselny i życzenia", "", time(22, 0), time(23, 0), "Sala Główna", 7),
            ("Kontynuacja zabawy", "", time(23, 0), time(2, 0), "Parkiet", 8),
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

        # Create menu items
        menu_data = [
            # Welcome drinks
            ("Prosecco z malinami", "Musujące wino z dodatkiem świeżych malin i mięty", "welcome", None, "", False, 1),
            ("Canapé z łososiem", "Minibagietka z kremem serowym, wędzonym łososiem i kaparami", "welcome", None, "ryby", False, 2),
            
            # Appetizers
            ("Tatar z łososia", "Świeży łosoś z awokado, kaparami i sosem musztardowo-miodowym", "appetizer", 25.00, "ryby", False, 1),
            ("Carpaccio z polędwicy", "Cienkie plastry polędwicy z rukolą i parmezanem", "appetizer", 28.00, "", False, 2),
            
            # Soups
            ("Żurek staropolski", "Tradycyjny żurek z białą kiełbasą i jajkiem w chlebowym garnku", "soup", 15.00, "gluten", False, 1),
            ("Krem z dyni", "Aksamitny krem z pieczonych dyni z imbirem", "soup", 12.00, "", True, 2),
            
            # Main dishes
            ("Polędwica wieprzowa", "Polędwica w ziołach z grillowanymi warzywami i ziemniakami z rozmarynem", "main", 45.00, "", False, 1),
            ("Filet z łososia", "Grillowany filet z łososia z sosem cytrynowym", "main", 48.00, "ryby", False, 2),
            ("Risotto z grzybami", "Kremowe risotto z mieszanką grzybów leśnych", "main", 35.00, "", True, 3),
            
            # Desserts
            ("Tiramisu", "Klasyczne tiramisu z mascarpone i kawą", "dessert", 18.00, "jaja, mleko", False, 1),
            ("Tort weselny", "Trzypiętrowy tort z kremem waniliowym i owocami leśnymi", "dessert", None, "gluten, mleko, jaja", False, 2),
            ("Sorbet owocowy", "Sorbet z owoców sezonowych", "dessert", 12.00, "", True, 3),
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
                'Sample login credentials:\n'
                '  Username: jan.kowalski, Password: wesele2024\n'
                '  Username: maria.nowak, Password: wesele2024\n'
                '  (and others...)\n'
            )
        )