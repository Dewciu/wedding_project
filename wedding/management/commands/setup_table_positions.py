from django.core.management.base import BaseCommand
from wedding.models import Table

class Command(BaseCommand):
    help = 'Setup default table positions for the wedding map'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing table positions',
        )
        parser.add_argument(
            '--layout',
            type=str,
            choices=['default', 'classic', 'modern'],
            default='default',
            help='Choose table layout style',
        )

    def handle(self, *args, **options):
        force = options['force']
        layout = options['layout']
        
        self.stdout.write(f'Setting up table positions with "{layout}" layout...')

        # Define table positions based on layout
        if layout == 'default':
            positions = self.get_default_positions()
        elif layout == 'classic':
            positions = self.get_classic_positions()
        elif layout == 'modern':
            positions = self.get_modern_positions()

        updated_count = 0
        created_count = 0

        for table_data in positions:
            try:
                table, created = Table.objects.get_or_create(
                    number=table_data['number'],
                    defaults={
                        'name': table_data.get('name', f"Stół {table_data['number']}"),
                        'capacity': table_data.get('capacity', 8),
                        'description': table_data.get('description', ''),
                        'map_x': table_data['map_x'],
                        'map_y': table_data['map_y'],
                        'map_width': table_data['map_width'],
                        'map_height': table_data['map_height'],
                        'shape': table_data['shape'],
                        'color': table_data.get('color', '#d4c4a8'),
                        'border_color': table_data.get('border_color', '#b8a082'),
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(f'✓ Created table {table.number} at ({table.map_x}, {table.map_y})')
                elif force:
                    # Update existing table
                    table.map_x = table_data['map_x']
                    table.map_y = table_data['map_y']
                    table.map_width = table_data['map_width']
                    table.map_height = table_data['map_height']
                    table.shape = table_data['shape']
                    table.color = table_data.get('color', table.color)
                    table.border_color = table_data.get('border_color', table.border_color)
                    table.save()
                    updated_count += 1
                    self.stdout.write(f'✓ Updated table {table.number} position')
                else:
                    self.stdout.write(f'- Table {table.number} already exists (use --force to update)')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing table {table_data["number"]}: {e}')
                )

        self.stdout.write('\n' + '='*50)
        self.stdout.write('TABLE POSITIONING SETUP COMPLETE')
        self.stdout.write('='*50)
        self.stdout.write(f'Created: {created_count} tables')
        self.stdout.write(f'Updated: {updated_count} tables')
        self.stdout.write('\nYou can now:')
        self.stdout.write('1. Visit Django Admin to fine-tune positions')
        self.stdout.write('2. Test the interactive map')
        self.stdout.write('3. Adjust colors and shapes as needed')

    def get_default_positions(self):
        """Chessboard pattern layout with rectangular perimeter tables"""
        return [
            # Top rectangular table
            {
                'number': 2,
                'name': 'Stolik “Nie Dotykać Tortu”',
                'map_x': 425, 'map_y': 125,
                'map_width': 350, 'map_height': 70,
                'shape': 'rectangular',
                'capacity': 50,
                'description': 'Rodzina ze strony Pana Młodego',
                'color': '#d4a574',
                'border_color': '#8b6f47'
            },
            
            # Left rectangular table
            {
                'number': 1,
                'name': 'Stół Pary Młodej',
                'map_x': 125, 'map_y': 300,
                'map_width': 60, 'map_height': 200,
                'shape': 'rectangular',
                'capacity': 5,
                'description': 'Goście specjalni',
                'color': '#d4a574',
                'border_color': '#8b6f47'
            },

            # Bottom rectangular table
            {
                'number': 3,
                'name': 'Stolik “Ostatnia Kolejka”',
                'map_x': 450, 'map_y': 475,
                'map_width': 400, 'map_height': 60,
                'shape': 'rectangular',
                'capacity': 32,
                'description': 'Para Młoda i najbliżsi',
                'color': '#d4a574',
                'border_color': '#8b6f47'
            },

            # Chessboard pattern - Row 1
            {
                'number': 4,
                'name': 'Stolik “Zaraz Wracam”',
                'map_x': 250, 'map_y': 260,
                'map_width': 80, 'map_height': 80,
                'shape': 'circular',
                'capacity': 8,
                'color': '#d4a574',
                'border_color': '#8b6f47'
            },
            {
                'number': 6,
                'name': 'Stolik “Pół Na Pół”',
                'map_x': 400, 'map_y': 260,
                'map_width': 80, 'map_height': 80,
                'shape': 'circular',
                'capacity': 8,
                'color': '#d4a574',
                'border_color': '#8b6f47'
            },
            {
                'number': 8,
                'name': 'Stolik “Obróć Panną”',
                'map_x': 550, 'map_y': 260,
                'map_width': 80, 'map_height': 80,
                'shape': 'circular',
                'capacity': 8,
                'color': '#d4a574',
                'border_color': '#8b6f47'
            },
            {
                'number': 10,
                'name': 'Stolik “BMW - Będziesz Miał Wesele”',
                'map_x': 700, 'map_y': 260,
                'map_width': 80, 'map_height': 80,
                'shape': 'circular',
                'capacity': 8,
                'color': '#d4a574',
                'border_color': '#8b6f47'
            },

            # Chessboard pattern - Row 2 (offset)
            {
                'number': 5,
                'name': 'Stolik “Nie Mów Mamie”',
                'map_x': 325, 'map_y': 340,
                'map_width': 80, 'map_height': 80,
                'shape': 'circular',
                'capacity': 10,
                'color': '#d4a574',
                'border_color': '#8b6f47'
            },
            {
                'number': 7,
                'name': 'Stolik “Operacja Barszcz”',
                'map_x': 475, 'map_y': 340,
                'map_width': 80, 'map_height': 80,
                'shape': 'circular',
                'capacity': 10,
                'color': '#d4a574',
                'border_color': '#8b6f47'
            },
            {
                'number': 9,
                'name': 'Stolik “Wszystko pod Kontrolą”',
                'map_x': 625, 'map_y': 340,
                'map_width': 80, 'map_height': 80,
                'shape': 'circular',
                'capacity': 10,
                'color': '#d4a574',
                'border_color': '#8b6f47'
            }
        ]

    def get_classic_positions(self):
        """Classic symmetric layout"""
        return [
            # Head table
            {'number': 1, 'map_x': 450, 'map_y': 100, 'map_width': 400, 'map_height': 80, 'shape': 'rectangular', 'capacity': 12},
            
            # Two columns of round tables
            {'number': 2, 'map_x': 200, 'map_y': 250, 'map_width': 90, 'map_height': 90, 'shape': 'circular', 'capacity': 8},
            {'number': 3, 'map_x': 700, 'map_y': 250, 'map_width': 90, 'map_height': 90, 'shape': 'circular', 'capacity': 8},
            {'number': 4, 'map_x': 200, 'map_y': 400, 'map_width': 90, 'map_height': 90, 'shape': 'circular', 'capacity': 8},
            {'number': 5, 'map_x': 700, 'map_y': 400, 'map_width': 90, 'map_height': 90, 'shape': 'circular', 'capacity': 8},
            {'number': 6, 'map_x': 200, 'map_y': 550, 'map_width': 90, 'map_height': 90, 'shape': 'circular', 'capacity': 8},
            {'number': 7, 'map_x': 700, 'map_y': 550, 'map_width': 90, 'map_height': 90, 'shape': 'circular', 'capacity': 8},
            
            # Center tables
            {'number': 8, 'map_x': 350, 'map_y': 340, 'map_width': 80, 'map_height': 80, 'shape': 'circular', 'capacity': 6},
            {'number': 9, 'map_x': 550, 'map_y': 340, 'map_width': 80, 'map_height': 80, 'shape': 'circular', 'capacity': 6},
            {'number': 10, 'map_x': 450, 'map_y': 450, 'map_width': 80, 'map_height': 80, 'shape': 'circular', 'capacity': 6},
        ]

    def get_modern_positions(self):
        """Modern asymmetric layout"""
        return [
            # Sweetheart table
            {'number': 1, 'map_x': 450, 'map_y': 120, 'map_width': 120, 'map_height': 60, 'shape': 'rectangular', 'capacity': 2, 'color': '#f5f0e8'},
            
            # Family tables
            {'number': 2, 'map_x': 200, 'map_y': 220, 'map_width': 100, 'map_height': 100, 'shape': 'circular', 'capacity': 10},
            {'number': 3, 'map_x': 700, 'map_y': 220, 'map_width': 100, 'map_height': 100, 'shape': 'circular', 'capacity': 10},
            
            # Mixed shapes for visual interest
            {'number': 4, 'map_x': 150, 'map_y': 380, 'map_width': 80, 'map_height': 120, 'shape': 'rectangular', 'capacity': 8},
            {'number': 5, 'map_x': 350, 'map_y': 320, 'map_width': 85, 'map_height': 85, 'shape': 'circular', 'capacity': 8},
            {'number': 6, 'map_x': 550, 'map_y': 320, 'map_width': 85, 'map_height': 85, 'shape': 'circular', 'capacity': 8},
            {'number': 7, 'map_x': 750, 'map_y': 380, 'map_width': 120, 'map_height': 80, 'shape': 'rectangular', 'capacity': 8},
            
            # Back tables
            {'number': 8, 'map_x': 250, 'map_y': 500, 'map_width': 90, 'map_height': 90, 'shape': 'circular', 'capacity': 8},
            {'number': 9, 'map_x': 450, 'map_y': 480, 'map_width': 90, 'map_height': 90, 'shape': 'circular', 'capacity': 8},
            {'number': 10, 'map_x': 0, 'map_y': 0, 'map_width': 90, 'map_height': 90, 'shape': 'circular', 'capacity': 8},
        ]