import os
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

class Command(BaseCommand):
    help = 'Generate PWA icons and assets for the wedding app'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of existing assets',
        )

    def handle(self, *args, **options):
        # Create images directory if it doesn't exist
        images_dir = Path(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0]) / 'wedding' / 'images'
        images_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write('Generating PWA assets...')

        # Icon sizes to generate
        icon_sizes = [16, 32, 72, 96, 128, 144, 152, 192, 384, 512]
        
        # Generate base icon
        base_icon = self.create_base_icon()
        
        # Generate all icon sizes
        for size in icon_sizes:
            icon_path = images_dir / f'icon-{size}.png'
            favicon_path = images_dir / f'favicon-{size}x{size}.png'
            
            if not icon_path.exists() or options['force']:
                resized_icon = base_icon.resize((size, size), Image.Resampling.LANCZOS)
                resized_icon.save(icon_path, 'PNG', optimize=True)
                self.stdout.write(f'✓ Generated {icon_path.name}')
                
                # Also save as favicon for smaller sizes
                if size in [16, 32]:
                    resized_icon.save(favicon_path, 'PNG', optimize=True)

        # Generate Apple touch icon
        apple_icon_path = images_dir / 'apple-touch-icon.png'
        if not apple_icon_path.exists() or options['force']:
            apple_icon = base_icon.resize((180, 180), Image.Resampling.LANCZOS)
            apple_icon.save(apple_icon_path, 'PNG', optimize=True)
            self.stdout.write(f'✓ Generated {apple_icon_path.name}')

        # Generate OG image
        og_image_path = images_dir / 'og-image.png'
        if not og_image_path.exists() or options['force']:
            og_image = self.create_og_image()
            og_image.save(og_image_path, 'PNG', optimize=True)
            self.stdout.write(f'✓ Generated {og_image_path.name}')

        # Generate screenshot placeholders
        self.generate_screenshots(images_dir, options['force'])

        # Generate shortcut icons
        self.generate_shortcut_icons(images_dir, options['force'])

        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 PWA assets generated successfully!\n'
                f'Assets saved to: {images_dir}\n'
                'Your wedding app is now ready for PWA installation.'
            )
        )

    def create_base_icon(self):
        """Create the base wedding app icon"""
        # Create a 512x512 canvas
        size = 512
        image = Image.new('RGBA', (size, size), color=(245, 240, 232, 255))
        draw = ImageDraw.Draw(image)

        # Draw wedding rings
        ring_color = (139, 111, 71, 255)  # #8b6f47
        ring_width = 25

        # Left ring
        left_ring_center = (size // 2 - 60, size // 2)
        draw.ellipse(
            [left_ring_center[0] - 80, left_ring_center[1] - 80,
             left_ring_center[0] + 80, left_ring_center[1] + 80],
            outline=ring_color, width=ring_width
        )

        # Right ring (overlapping)
        right_ring_center = (size // 2 + 60, size // 2)
        draw.ellipse(
            [right_ring_center[0] - 80, right_ring_center[1] - 80,
             right_ring_center[0] + 80, right_ring_center[1] + 80],
            outline=ring_color, width=ring_width
        )

        # Add hearts
        heart_color = (212, 165, 116, 255)  # #d4a574
        heart_size = 30
        
        # Simple heart shape using circles and triangle
        heart_x, heart_y = size // 2, size // 2 + 120
        
        # Heart circles (top)
        draw.ellipse([heart_x - 25, heart_y - 15, heart_x - 5, heart_y + 5], fill=heart_color)
        draw.ellipse([heart_x + 5, heart_y - 15, heart_x + 25, heart_y + 5], fill=heart_color)
        
        # Heart triangle (bottom)
        draw.polygon([
            (heart_x - 25, heart_y - 5),
            (heart_x + 25, heart_y - 5),
            (heart_x, heart_y + 25)
        ], fill=heart_color)

        return image

    def create_og_image(self):
        """Create Open Graph image for social sharing"""
        width, height = 1200, 630
        image = Image.new('RGB', (width, height), color=(245, 240, 232))
        draw = ImageDraw.Draw(image)

        # Background gradient effect
        for i in range(height):
            color_ratio = i / height
            r = int(245 * (1 - color_ratio) + 232 * color_ratio)
            g = int(240 * (1 - color_ratio) + 221 * color_ratio)
            b = int(232 * (1 - color_ratio) + 212 * color_ratio)
            draw.rectangle([0, i, width, i + 1], fill=(r, g, b))

        # Title
        try:
            # Try to use a nice font if available
            title_font = ImageFont.truetype("arial.ttf", 80)
            subtitle_font = ImageFont.truetype("arial.ttf", 40)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()

        title_text = "Nasze Wesele"
        subtitle_text = "Aplikacja Weselna"

        # Get text bounding boxes
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)

        # Center text
        title_x = (width - (title_bbox[2] - title_bbox[0])) // 2
        title_y = height // 2 - 80
        
        subtitle_x = (width - (subtitle_bbox[2] - subtitle_bbox[0])) // 2
        subtitle_y = title_y + 100

        # Draw text with shadow
        shadow_color = (93, 78, 55)
        text_color = (139, 111, 71)

        # Shadow
        draw.text((title_x + 3, title_y + 3), title_text, font=title_font, fill=shadow_color)
        draw.text((subtitle_x + 2, subtitle_y + 2), subtitle_text, font=subtitle_font, fill=shadow_color)

        # Main text
        draw.text((title_x, title_y), title_text, font=title_font, fill=text_color)
        draw.text((subtitle_x, subtitle_y), subtitle_text, font=subtitle_font, fill=text_color)

        # Decorative elements
        self.draw_decorative_pattern(draw, width, height)

        return image

    def draw_decorative_pattern(self, draw, width, height):
        """Draw decorative pattern on OG image"""
        # Draw some hearts in corners
        heart_color = (212, 165, 116, 100)  # Semi-transparent
        
        positions = [
            (100, 100), (width - 100, 100),
            (100, height - 100), (width - 100, height - 100)
        ]
        
        for x, y in positions:
            # Simple heart
            draw.ellipse([x - 15, y - 10, x + 5, y + 10], fill=heart_color)
            draw.ellipse([x - 5, y - 10, x + 15, y + 10], fill=heart_color)
            draw.polygon([(x - 15, y), (x + 15, y), (x, y + 20)], fill=heart_color)

    def generate_screenshots(self, images_dir, force=False):
        """Generate screenshot placeholders"""
        # Mobile screenshot
        mobile_path = images_dir / 'screenshot-mobile.png'
        if not mobile_path.exists() or force:
            mobile_screenshot = Image.new('RGB', (390, 844), color=(245, 240, 232))
            draw = ImageDraw.Draw(mobile_screenshot)
            
            # Simple mockup
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 100), "Nasze Wesele", font=font, fill=(139, 111, 71))
            draw.text((50, 150), "Galeria Zdjęć", font=font, fill=(93, 78, 55))
            
            # Mock navigation
            nav_items = ["🏠 Strona Główna", "📷 Galeria", "🪑 Stoliki", "⏰ Harmonogram"]
            for i, item in enumerate(nav_items):
                y = 250 + i * 60
                draw.rectangle([30, y, 360, y + 45], fill=(212, 196, 168))
                draw.text((50, y + 10), item, font=font, fill=(93, 78, 55))
            
            mobile_screenshot.save(mobile_path, 'PNG')
            self.stdout.write(f'✓ Generated {mobile_path.name}')

        # Tablet screenshot
        tablet_path = images_dir / 'screenshot-tablet.png'
        if not tablet_path.exists() or force:
            tablet_screenshot = Image.new('RGB', (768, 1024), color=(245, 240, 232))
            tablet_screenshot.save(tablet_path, 'PNG')
            self.stdout.write(f'✓ Generated {tablet_path.name}')

    def generate_shortcut_icons(self, images_dir, force=False):
        """Generate shortcut icons"""
        shortcuts = [
            ('gallery-icon.png', '📷', 'Galeria'),
            ('upload-icon.png', '⬆️', 'Prześlij'),
            ('table-icon.png', '🪑', 'Stoliki'),
            ('schedule-icon.png', '⏰', 'Harmonogram')
        ]

        for filename, emoji, text in shortcuts:
            icon_path = images_dir / filename
            if not icon_path.exists() or force:
                icon = Image.new('RGBA', (96, 96), color=(245, 240, 232, 255))
                draw = ImageDraw.Draw(icon)
                
                # Draw background circle
                draw.ellipse([8, 8, 88, 88], fill=(212, 196, 168, 255), outline=(139, 111, 71, 255), width=2)
                
                try:
                    font = ImageFont.truetype("arial.ttf", 32)
                except:
                    font = ImageFont.load_default()
                
                # Center emoji/text
                bbox = draw.textbbox((0, 0), emoji, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (96 - text_width) // 2
                y = (96 - text_height) // 2
                
                draw.text((x, y), emoji, font=font, fill=(93, 78, 55, 255))
                
                icon.save(icon_path, 'PNG')
                self.stdout.write(f'✓ Generated {filename}')