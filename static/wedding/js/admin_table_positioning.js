// Admin Table Positioning JavaScript
(function($) {
    'use strict';

    $(document).ready(function() {
        if ($('body').hasClass('change-form') || $('body').hasClass('add-form')) {
            initTablePositioning();
        }
    });

    function initTablePositioning() {
        // Add positioning help and preview
        addPositioningHelp();
        addPositionPreview();
        
        // Setup real-time preview updates
        setupPreviewUpdates();
        
        // Add coordinate helpers
        addCoordinateHelpers();
    }

    function addPositioningHelp() {
        const helpHTML = `
            <div class="positioning-help">
                <strong>💡 Wskazówki pozycjonowania:</strong>
                <ul>
                    <li><strong>X:</strong> 0-900 (lewo-prawo), <strong>Y:</strong> 0-600 (góra-dół)</li>
                    <li>Centrum mapy: X=450, Y=300</li>
                    <li>Okrągłe stoliki: szerokość = wysokość (np. 85x85)</li>
                    <li>Prostokątne stoliki: różne wymiary (np. 200x65)</li>
                    <li>Większe wartości = większy stół na mapie</li>
                </ul>
            </div>
        `;
        
        $('.field-map_x').parent().prepend(helpHTML);
    }

    function addPositionPreview() {
        const previewHTML = `
            <div class="position-preview">
                <h4>🎯 Podgląd pozycji na mapie:</h4>
                <div class="mini-map" id="mini-map">
                    <div class="mini-table" id="preview-table">1</div>
                </div>
                <small style="color: #666;">
                    Podgląd jest orientacyjny. Rzeczywista mapa może wyglądać nieco inaczej.
                </small>
            </div>
        `;
        
        $('.field-shape').parent().after(previewHTML);
        updatePreview();
    }

    function setupPreviewUpdates() {
        const inputs = $('#id_map_x, #id_map_y, #id_map_width, #id_map_height, #id_shape, #id_color, #id_border_color, #id_number');
        
        inputs.on('input change', function() {
            updatePreview();
        });
        
        // Validate coordinates
        $('#id_map_x').on('change', function() {
            const val = parseFloat($(this).val());
            if (val < 0 || val > 900) {
                alert('Pozycja X powinna być między 0 a 900');
                $(this).focus();
            }
        });
        
        $('#id_map_y').on('change', function() {
            const val = parseFloat($(this).val());
            if (val < 0 || val > 600) {
                alert('Pozycja Y powinna być między 0 a 600');
                $(this).focus();
            }
        });
    }

    function updatePreview() {
        const x = parseFloat($('#id_map_x').val()) || 450;
        const y = parseFloat($('#id_map_y').val()) || 300;
        const width = parseFloat($('#id_map_width').val()) || 85;
        const height = parseFloat($('#id_map_height').val()) || 85;
        const shape = $('#id_shape').val() || 'circular';
        const color = $('#id_color').val() || '#d4c4a8';
        const borderColor = $('#id_border_color').val() || '#b8a082';
        const number = $('#id_number').val() || '1';

        const miniMap = $('#mini-map');
        const previewTable = $('#preview-table');

        // Scale coordinates for mini map (400x200 vs 900x600)
        const scaleX = 400 / 900;
        const scaleY = 200 / 600;
        
        const scaledX = x * scaleX;
        const scaledY = y * scaleY;
        const scaledWidth = Math.max(width * scaleX, 20); // Min 20px for visibility
        const scaledHeight = Math.max(height * scaleY, 20);

        // Update table preview
        previewTable.css({
            left: (scaledX - scaledWidth/2) + 'px',
            top: (scaledY - scaledHeight/2) + 'px',
            width: scaledWidth + 'px',
            height: scaledHeight + 'px',
            backgroundColor: color,
            borderColor: borderColor,
            borderRadius: shape === 'circular' ? '50%' : (shape === 'square' ? '6px' : '6px')
        });
        
        previewTable.removeClass('circular rectangular square').addClass(shape);
        previewTable.text(number);

        // Show coordinates info
        const coordInfo = `(${x}, ${y}) - ${width}×${height}px`;
        if (!$('.coord-info').length) {
            miniMap.after(`<small class="coord-info" style="color: #666; font-style: italic;">${coordInfo}</small>`);
        } else {
            $('.coord-info').text(coordInfo);
        }
    }

    function addCoordinateHelpers() {
        // Add unit indicators
        const coordinateFields = ['#id_map_x', '#id_map_y', '#id_map_width', '#id_map_height'];
        
        coordinateFields.forEach(function(selector) {
            const $field = $(selector);
            const $wrapper = $field.parent();
            
            $wrapper.addClass('coordinate-input');
            $field.after('<span class="coordinate-unit">px</span>');
        });

        // Add preset buttons for common positions
        const presetsHTML = `
            <div style="margin: 10px 0;">
                <strong>⚡ Szybkie pozycje:</strong><br>
                <button type="button" class="preset-btn" data-x="150" data-y="150">Lewy górny</button>
                <button type="button" class="preset-btn" data-x="450" data-y="150">Środek górny</button>
                <button type="button" class="preset-btn" data-x="750" data-y="150">Prawy górny</button><br>
                <button type="button" class="preset-btn" data-x="150" data-y="300">Lewy środek</button>
                <button type="button" class="preset-btn" data-x="450" data-y="300">Centrum</button>
                <button type="button" class="preset-btn" data-x="750" data-y="300">Prawy środek</button><br>
                <button type="button" class="preset-btn" data-x="150" data-y="450">Lewy dolny</button>
                <button type="button" class="preset-btn" data-x="450" data-y="450">Środek dolny</button>
                <button type="button" class="preset-btn" data-x="750" data-y="450">Prawy dolny</button>
            </div>
        `;
        
        $('.field-map_y').parent().after(presetsHTML);
        
        // Style preset buttons
        $('.preset-btn').css({
            'background': '#8b6f47',
            'color': 'white',
            'border': 'none',
            'padding': '4px 8px',
            'margin': '2px',
            'border-radius': '4px',
            'cursor': 'pointer',
            'font-size': '11px'
        });
        
        $('.preset-btn').hover(
            function() { $(this).css('background', '#5d4e37'); },
            function() { $(this).css('background', '#8b6f47'); }
        );
        
        $('.preset-btn').click(function() {
            const x = $(this).data('x');
            const y = $(this).data('y');
            
            $('#id_map_x').val(x);
            $('#id_map_y').val(y);
            updatePreview();
        });

        // Add size presets
        const sizePresetsHTML = `
            <div style="margin: 10px 0;">
                <strong>📏 Szybkie rozmiary:</strong><br>
                <button type="button" class="size-preset-btn" data-w="85" data-h="85" data-shape="circular">Mały okrągły</button>
                <button type="button" class="size-preset-btn" data-w="100" data-h="100" data-shape="circular">Duży okrągły</button>
                <button type="button" class="size-preset-btn" data-w="150" data-h="70" data-shape="rectangular">Prostokąt poziomy</button>
                <button type="button" class="size-preset-btn" data-w="70" data-h="150" data-shape="rectangular">Prostokąt pionowy</button>
            </div>
        `;
        
        $('.field-map_height').parent().after(sizePresetsHTML);
        
        $('.size-preset-btn').css({
            'background': '#d4c4a8',
            'color': '#5d4e37',
            'border': '1px solid #b8a082',
            'padding': '4px 8px',
            'margin': '2px',
            'border-radius': '4px',
            'cursor': 'pointer',
            'font-size': '11px'
        });
        
        $('.size-preset-btn').click(function() {
            $('#id_map_width').val($(this).data('w'));
            $('#id_map_height').val($(this).data('h'));
            $('#id_shape').val($(this).data('shape'));
            updatePreview();
        });
    }

})(django.jQuery);