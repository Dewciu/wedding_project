import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wedding.models import Guest, Table
from django.db import transaction

class Command(BaseCommand):
    help = 'Import guests from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file with guests',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true', 
            help='Update existing guests if they already exist',
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        dry_run = options['dry_run']
        update_existing = options['update_existing']
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_file_path}')
            )
            return

        # Statistics
        stats = {
            'created': 0,
            'updated': 0,
            'errors': 0,
            'skipped': 0
        }

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter
                first_line = file.readline()
                file.seek(0)
                
                delimiter = ';' if ';' in first_line else ','
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Normalize CSV headers to remove BOM and whitespace
                normalized_fieldnames = [h.strip().replace('\ufeff', '') for h in reader.fieldnames]
                reader.fieldnames = normalized_fieldnames

                # Map CSV headers to expected fields
                header_mapping = {
                    'Firstname': 'first_name',
                    'Lastname': 'last_name', 
                    'Table': 'table_number',
                    '*Typ*': 'guest_type'
                }
                
                with transaction.atomic():
                    for row_num, row in enumerate(reader, start=2):
                        try:
                            # Map headers
                            mapped_row = {}
                            for csv_header, field in header_mapping.items():
                                # Use normalized header names
                                for key in row.keys():
                                    if key.strip().replace('\ufeff', '') == csv_header:
                                        mapped_row[field] = row[key].strip()
                            print(mapped_row)
                            first_name = mapped_row.get('first_name', '').strip()
                            last_name = mapped_row.get('last_name', '').strip()
                            table_str = mapped_row.get('table_number', '').strip()
                            guest_type = mapped_row.get('guest_type', '').strip()

                            print(f"Processing row {row_num}: {first_name} {last_name}, Table: {table_str}, Type: {guest_type}")

                            # Skip empty rows or rows with missing essential data
                            if not first_name and not last_name:
                                stats['skipped'] += 1
                                continue
                                
                            # Handle special cases like "osoba towarzysząca"
                            if first_name.lower().startswith('osoba towarzysząca') or 'towarzysząca' in guest_type:
                                # Extract the main guest's name from the last name field
                                if last_name and last_name != '':
                                    first_name = f"Osoba towarzysząca {last_name}"
                                    last_name = "Towarzyszaca"
                                else:
                                    first_name = "Osoba towarzysząca"
                                    last_name = "Nieznana"
                            
                            # Handle empty names for service staff
                            if not first_name.strip():
                                if 'fotograf' in last_name.lower():
                                    first_name = last_name
                                    last_name = "Fotograf"
                                elif 'dj' in last_name.lower():
                                    first_name = "DJ"
                                    last_name = "Obsługa"
                                else:
                                    first_name = "Gość"
                            
                            if not last_name.strip():
                                last_name = "Nieznany"
                            
                            # Parse table number
                            table_number = None
                            if table_str and table_str.isdigit():
                                table_number = int(table_str)
                            elif table_str == '-1' or table_str == 'x':
                                table_number = None  # Not assigned yet
                                
                            # Generate username
                            base_username = f"{first_name.lower().replace(' ', '_')}.{last_name.lower().replace(' ', '_')}"
                            base_username = base_username.replace('ą', 'a').replace('ć', 'c').replace('ę', 'e').replace('ł', 'l').replace('ń', 'n').replace('ó', 'o').replace('ś', 's').replace('ź', 'z').replace('ż', 'z')
                            
                            username = base_username
                            counter = 1
                            while User.objects.filter(username=username).exists() and not update_existing:
                                username = f"{base_username}{counter}"
                                counter += 1
                            
                            if dry_run:
                                self.stdout.write(
                                    f"Would create: {first_name} {last_name} (username: {username}) -> Stół: {table_number or 'nie przypisany'}"
                                )
                                stats['created'] += 1
                                continue
                            
                            # Check if user already exists
                            existing_user = None
                            try:
                                existing_user = User.objects.get(username=username)
                            except User.DoesNotExist:
                                pass
                            
                            if existing_user and not update_existing:
                                self.stdout.write(
                                    self.style.WARNING(f'User {username} already exists. Skipping...')
                                )
                                stats['skipped'] += 1
                                continue
                            
                            # Create or update user
                            if existing_user and update_existing:
                                user = existing_user
                                user.first_name = first_name
                                user.last_name = last_name
                                user.email = f"{username}@example.com"
                                user.save()
                                
                                # Update guest
                                guest, created = Guest.objects.get_or_create(user=user)
                                guest.table_number = table_number
                                guest.save()
                                
                                stats['updated'] += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f'Updated: {user.get_full_name()} -> Stół: {table_number or "nie przypisany"}')
                                )
                            else:
                                # Create new user
                                user = User.objects.create_user(
                                    username=username,
                                    first_name=first_name,
                                    last_name=last_name,
                                    email=f"{username}@example.com",
                                    password="wesele2024"  # Default password
                                )
                                
                                # Create guest profile
                                guest = Guest.objects.create(
                                    user=user,
                                    table_number=table_number,
                                    phone_number="",
                                    confirmed=True
                                )
                                
                                stats['created'] += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f'Created: {user.get_full_name()} -> Stół: {table_number or "nie przypisany"}')
                                )
                        
                        except Exception as e:
                            stats['errors'] += 1
                            self.stdout.write(
                                self.style.ERROR(f'Error processing row {row_num}: {e}')
                            )
                            self.stdout.write(f'Row data: {row}')
                            continue

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading CSV file: {e}')
            )
            return

        # Print summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('IMPORT SUMMARY')
        self.stdout.write('='*50)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes were made'))
        
        self.stdout.write(f'Created: {stats["created"]}')
        self.stdout.write(f'Updated: {stats["updated"]}')
        self.stdout.write(f'Skipped: {stats["skipped"]}')
        self.stdout.write(f'Errors: {stats["errors"]}')
        
        total_processed = stats['created'] + stats['updated'] + stats['skipped'] + stats['errors']
        self.stdout.write(f'Total processed: {total_processed}')
        
        if not dry_run and (stats['created'] > 0 or stats['updated'] > 0):
            self.stdout.write('\n' + self.style.SUCCESS('✓ Import completed successfully!'))
            self.stdout.write('Default password for all guests: wesele2024')
            
            # Show table occupancy summary
            self.stdout.write('\n' + '='*30)
            self.stdout.write('TABLE OCCUPANCY SUMMARY')
            self.stdout.write('='*30)
            
            tables = Table.objects.all().order_by('number')
            for table in tables:
                guest_count = Guest.objects.filter(table_number=table.number).count()
                self.stdout.write(f'Stół {table.number}: {guest_count}/{table.capacity} gości')
            
            # Show guests without table assignment
            unassigned_count = Guest.objects.filter(table_number__isnull=True).count()
            if unassigned_count > 0:
                self.stdout.write(f'\nGoście bez przypisania do stołu: {unassigned_count}')
        
        self.stdout.write('\n' + 'Use --dry-run to preview changes before importing')
        self.stdout.write('Use --update-existing to update existing guests')