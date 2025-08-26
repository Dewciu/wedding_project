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

        # Create realistic guest data
        guest_data = [
            # Stół 1 - Rodzina Panny Młodej
            ("Jadwiga", "Kowalska", "jadwiga.kowalska", "123456789", 1),
            ("Stanisław", "Kowalski", "stanislaw.kowalski", "123456790", 1),
            ("Maria", "Nowak", "maria.nowak", "123456791", 1),
            ("Krzysztof", "Nowak", "krzysztof.nowak", "123456792", 1),
            ("Magdalena", "Wójcik", "magdalena.wojcik", "123456793", 1),
            ("Tomasz", "Wójcik", "tomasz.wojcik", "123456794", 1),
            ("Barbara", "Kowalczyk", "barbara.kowalczyk", "123456795", 1),
            ("Jerzy", "Kowalczyk", "jerzy.kowalczyk", "123456796", 1),
            ("Agnieszka", "Lewandowska", "agnieszka.lewandowska", "123456797", 1),
            ("Piotr", "Lewandowski", "piotr.lewandowski", "123456798", 1),

            # Stół 2 - Rodzina Pana Młodego  
            ("Helena", "Wiśniewska", "helena.wisniewska", "223456789", 2),
            ("Jan", "Wiśniewski", "jan.wisniewski", "223456790", 2),
            ("Elżbieta", "Dąbrowska", "elzbieta.dabrowska", "223456791", 2),
            ("Marek", "Dąbrowski", "marek.dabrowski", "223456792", 2),
            ("Teresa", "Jankowska", "teresa.jankowska", "223456793", 2),
            ("Andrzej", "Jankowski", "andrzej.jankowski", "223456794", 2),
            ("Zofia", "Mazur", "zofia.mazur", "223456795", 2),
            ("Władysław", "Mazur", "wladyslaw.mazur", "223456796", 2),
            ("Danuta", "Krawczyk", "danuta.krawczyk", "223456797", 2),
            ("Tadeusz", "Krawczyk", "tadeusz.krawczyk", "223456798", 2),

            # Stół 3 - Przyjaciele ze Studiów
            ("Karolina", "Zielińska", "karolina.zielinska", "323456789", 3),
            ("Paweł", "Zieliński", "pawel.zielinski", "323456790", 3),
            ("Natalia", "Szymańska", "natalia.szymanska", "323456791", 3),
            ("Michał", "Szymański", "michal.szymanski", "323456792", 3),
            ("Iwona", "Woźniak", "iwona.wozniak", "323456793", 3),
            ("Robert", "Woźniak", "robert.wozniak", "323456794", 3),
            ("Ewa", "Kozłowska", "ewa.kozlowska", "323456795", 3),
            ("Grzegorz", "Kozłowski", "grzegorz.kozlowski", "323456796", 3),

            # Stół 4 - Znajomi z Pracy
            ("Anna", "Jankowska", "anna.jankowska2", "423456789", 4),
            ("Łukasz", "Jankowski", "lukasz.jankowski", "423456790", 4),
            ("Katarzyna", "Wojciechowska", "katarzyna.wojciechowska", "423456791", 4),
            ("Rafał", "Wojciechowski", "rafal.wojciechowski", "423456792", 4),
            ("Beata", "Kwiatkowska", "beata.kwiatkowska", "423456793", 4),
            ("Marcin", "Kwiatkowski", "marcin.kwiatkowski", "423456794", 4),
            ("Justyna", "Kaczmarek", "justyna.kaczmarek", "423456795", 4),
            ("Damian", "Kaczmarek", "damian.kaczmarek", "423456796", 4),

            # Stół 5 - Przyjaciele z Dzieciństwa
            ("Monika", "Piotrowska", "monika.piotrowska", "523456789", 5),
            ("Sebastian", "Piotrowski", "sebastian.piotrowski", "523456790", 5),
            ("Sylwia", "Grabowska", "sylwia.grabowska", "523456791", 5),
            ("Jacek", "Grabowski", "jacek.grabowski", "523456792", 5),
            ("Aleksandra", "Nowakowska", "aleksandra.nowakowska", "523456793", 5),
            ("Kamil", "Nowakowski", "kamil.nowakowski", "523456794", 5),
            ("Dorota", "Wieczorek", "dorota.wieczorek", "523456795", 5),
            ("Artur", "Wieczorek", "artur.wieczorek", "523456796", 5),

            # Stół 6 - Sąsiedzi i Znajomi
            ("Halina", "Majewska", "halina.majewska", "623456789", 6),
            ("Zbigniew", "Majewski", "zbigniew.majewski", "623456790", 6),
            ("Renata", "Olszewska", "renata.olszewska", "623456791", 6),
            ("Dariusz", "Olszewski", "dariusz.olszewski", "623456792", 6),
            ("Małgorzata", "Stępień", "malgorzata.stepien", "623456793", 6),
            ("Mariusz", "Stępień", "mariusz.stepien", "623456794", 6),
            ("Grażyna", "Jaworska", "grazyna.jaworska", "623456795", 6),
            ("Ryszard", "Jaworski", "ryszard.jaworski", "623456796", 6),

            # Stół 7 - Drużbowie i Druhny
            ("Paulina", "Adamska", "paulina.adamska", "723456789", 7),
            ("Filip", "Adamski", "filip.adamski", "723456790", 7),
            ("Weronika", "Dudek", "weronika.dudek", "723456791", 7),
            ("Bartosz", "Dudek", "bartosz.dudek", "723456792", 7),
            ("Joanna", "Rutkowska", "joanna.rutkowska", "723456793", 7),
            ("Mateusz", "Rutkowski", "mateusz.rutkowski", "723456794", 7),
            ("Patrycja", "Michalska", "patrycja.michalska", "723456795", 7),
            ("Konrad", "Michalski", "konrad.michalski", "723456796", 7),
            ("Izabela", "Sikora", "izabela.sikora", "723456797", 7),
            ("Adrian", "Sikora", "adrian.sikora", "723456798", 7),

            # Stół 8 - Młodzież
            ("Julia", "Bąk", "julia.bak", "823456789", 8),
            ("Kacper", "Bąk", "kacper.bak", "823456790", 8),
            ("Oliwia", "Król", "oliwia.krol", "823456791", 8),
            ("Jakub", "Król", "jakub.krol", "823456792", 8),
            ("Zuzanna", "Ptak", "zuzanna.ptak", "823456793", 8),
            ("Szymon", "Ptak", "szymon.ptak", "823456794", 8),
            ("Wiktoria", "Lis", "wiktoria.lis", "823456795", 8),
            ("Oskar", "Lis", "oskar.lis", "823456796", 8),
            ("Maja", "Wilk", "maja.wilk", "823456797", 8),
            ("Natan", "Wilk", "natan.wilk", "823456798", 8),

            # Stół 9 - Starsze Pokolenie
            ("Janina", "Maciejewska", "janina.maciejewska", "923456789", 9),
            ("Kazimierz", "Maciejewski", "kazimierz.maciejewski", "923456790", 9),
            ("Stanisława", "Urban", "stanislawa.urban", "923456791", 9),
            ("Józef", "Urban", "jozef.urban", "923456792", 9),
            ("Genowefa", "Sokół", "genowefa.sokol", "923456793", 9),
            ("Bolesław", "Sokół", "boleslaw.sokol", "923456794", 9),
            ("Irena", "Kalinowski", "irena.kalinowska", "923456795", 9),
            ("Mieczysław", "Kalinowski", "mieczyslaw.kalinowski", "923456796", 9),

            # Stół 10 - Stół Honorowy
            ("Anna", "Nowak", "anna.nowak", "para1", 10),  # Panna Młoda
            ("Marek", "Kowalski", "marek.kowalski", "para2", 10),  # Pan Młody
            ("Magdalena", "Świadkowa", "magdalena.swiadkowa", "1023456793", 10),
            ("Tomasz", "Świadek", "tomasz.swiadek", "1023456794", 10),
            ("Ksiądz", "Proboszcz", "ksiadz.proboszcz", "1023456795", 10),
            ("Fotograf", "Weselny", "fotograf.weselny", "1023456796", 10),
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

        # Create schedule events - bez zmian
        events_data = [
            ("Przybywanie gości, koktajl powitalny", "Powitanie gości, koktajle i przystawki", time(15, 0), time(15, 30), "Ogród", 1),
            ("Ceremonia ślubna", "Ślub cywilny w ogrodzie", time(15, 30), time(16, 30), "Ogród", 2),
            ("Sesja zdjęciowa i gratulacje", "Zdjęcia z rodziną i przyjaciółmi", time(16, 30), time(17, 30), "Ogród", 3),
            ("Obiad weselny", "Powitanie w sali, obiad", time(17, 30), time(19, 0), "Sala Główna", 4),
            ("Pierwszy taniec Pary Młodej", "", time(19, 0), time(19, 30), "Parkiet", 5),
            ("Rozpoczęcie zabawy tanecznej", "", time(19, 30), time(22, 0), "Parkiet", 6),
            ("Tort weselny i życzenia", "", time(22, 0), time(23, 0), "Sala Główna", 7),
            ("Kontynuacja zabavy", "", time(23, 0), time(2, 0), "Parkiet", 8),
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

        # Menu items - bez zmian
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
                'Utworzono 10 stolików z łączną liczbą ~90 gości\n'
                'Sample login credentials:\n'
                '  Username: jadwiga.kowalska, Password: wesele2024\n'
                '  Username: anna.nowak (Panna Młoda), Password: wesele2024\n'
                '  Username: marek.kowalski (Pan Młody), Password: wesele2024\n'
                '  (i inni...)\n'
            )
        )