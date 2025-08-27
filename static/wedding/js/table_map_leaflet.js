// Wedding Table Map - Fixed Responsive Version
class WeddingTableMap {
    constructor() {
        this.map = null;
        this.tableMarkers = {};
        this.guestMarkers = {};
        this.currentHighlighted = null;
        this.searchTimeout = null;
        this.currentGuestInfo = window.weddingData?.currentGuestInfo || null;
        this.mapBounds = { width: 900, height: 600 }; // Virtual coordinates
        
        console.log('🏗️ Initializing Wedding Table Map...');
        this.init();
    }

    init() {
        this.createMap();
        this.addTables();
        this.setupSearch();
        this.setupEventListeners();
        
        // Highlight current guest's table if found
        if (this.currentGuestInfo && this.currentGuestInfo.table_number) {
            setTimeout(() => {
                this.highlightTable(this.currentGuestInfo.table_number);
            }, 1000);
        }
    }

    createMap() {
        console.log('🗺️ Creating responsive Leaflet map...');
        
        const isMobile = window.innerWidth <= 768;
        console.log('📱 Mobile device:', isMobile);
        
        // Clear any existing map
        if (this.map) {
            this.map.remove();
        }

        this.map = L.map('wedding-map', {
            crs: L.CRS.Simple,
            minZoom: isMobile ? -2 : -1,
            maxZoom: isMobile ? 1 : 2,
            zoomControl: true,
            attributionControl: false,
            scrollWheelZoom: !isMobile, // Disable on mobile to prevent conflicts
            doubleClickZoom: true,
            touchZoom: isMobile,
            dragging: true,
            tap: isMobile,
            tapTolerance: isMobile ? 20 : 10, // Larger tolerance on mobile
            // CRITICAL: Prevent CSS transforms interfering
            renderer: L.canvas({ padding: 0.5 })
        });

        // Set bounds based on our virtual coordinate system
        const bounds = [[0, 0], [this.mapBounds.height, this.mapBounds.width]];
        this.map.fitBounds(bounds);
        this.map.setMaxBounds([[-50, -50], [this.mapBounds.height + 50, this.mapBounds.width + 50]]);

        // Custom zoom control positioning
        this.map.zoomControl.setPosition('topright');

        // Add venue background
        this.addVenueBackground();
        
        // Mobile-specific optimizations
        if (isMobile) {
            this.setupMobileOptimizations();
        }

        console.log('✅ Map created with bounds:', bounds);
    }

    addVenueBackground() {
        // Venue outline
        const venueOutline = L.rectangle([
            [50, 50], 
            [this.mapBounds.height - 50, this.mapBounds.width - 50]
        ], {
            color: '#d4c4a8',
            fillColor: '#f8f5f0',
            fillOpacity: 0.3,
            weight: 2,
            dashArray: '5, 5'
        }).addTo(this.map);
    }

    setupMobileOptimizations() {
        // Disable problematic interactions on mobile
        this.map.on('touchstart', (e) => {
            // Prevent accidental map panning when trying to tap markers
            if (e.originalEvent.touches.length === 1) {
                this.singleTouchStart = true;
                setTimeout(() => {
                    this.singleTouchStart = false;
                }, 300);
            }
        });

        // Add loading state
        const mapElement = document.getElementById('wedding-map');
        mapElement.classList.add('loading');
        setTimeout(() => {
            mapElement.classList.remove('loading');
        }, 1000);
    }

    addTables() {
        console.log('🪑 Adding tables with responsive positioning...');
        
        const tables = window.weddingData?.tables || [];
        console.log(`Found ${tables.length} tables`);
        
        if (tables.length === 0) {
            console.warn('No tables data - adding test tables');
            this.addTestTables();
            return;
        }
        
        tables.forEach(table => {
            try {
                this.createResponsiveTableMarker(table);
                console.log(`✅ Table ${table.number} added successfully`);
            } catch (error) {
                console.error(`❌ Error creating table ${table.number}:`, error);
            }
        });
    }

    createResponsiveTableMarker(table) {
        // Use database coordinates or fallbacks
        const x = parseFloat(table.map_x) || 450;
        const y = parseFloat(table.map_y) || 300;
        const width = parseFloat(table.map_width) || 85;
        const height = parseFloat(table.map_height) || 85;
        const shape = table.shape || 'circular';
        const color = table.color || '#d4c4a8';
        const borderColor = table.border_color || '#b8a082';

        // Convert to Leaflet coordinates (y, x)
        const coords = [y, x];
        const size = [width, height];
        const isHighlighted = this.currentGuestInfo && this.currentGuestInfo.table_number === table.number;

        // Colors
        const fillColor = isHighlighted ? '#5d4e37' : color;
        const strokeColor = isHighlighted ? '#2c1810' : borderColor;

        let tableMarker;

        // Create table shape
        if (shape === 'rectangular' || shape === 'square') {
            const bounds = [
                [y - height/2, x - width/2],
                [y + height/2, x + width/2]
            ];
            
            tableMarker = L.rectangle(bounds, {
                color: strokeColor,
                fillColor: fillColor,
                fillOpacity: 0.8,
                weight: 3,
                // CRITICAL: Disable CSS interactions that cause jumping
                interactive: true,
                bubblingMouseEvents: false,
                className: 'table-shape'
            }).addTo(this.map);

        } else {
            // Circular table
            tableMarker = L.circle(coords, {
                radius: Math.max(width, height) / 2,
                color: strokeColor,
                fillColor: fillColor,
                fillOpacity: 0.8,
                weight: 3,
                // CRITICAL: Disable CSS interactions
                interactive: true,
                bubblingMouseEvents: false,
                className: 'table-shape'
            }).addTo(this.map);
        }

        // Create table number label - SEPARATE from table shape
        const labelMarker = L.marker(coords, {
            icon: L.divIcon({
                className: 'table-number-marker',
                html: `<div class="table-number-label" style="
                    background: ${fillColor}; 
                    color: ${isHighlighted ? '#f5f0e8' : '#5d4e37'}; 
                    border: 2px solid ${strokeColor}; 
                    border-radius: ${shape === 'circular' ? '50%' : '6px'};
                    width: 40px; height: 40px;
                    display: flex; align-items: center; justify-content: center;
                    font-weight: bold; font-size: 1.2rem;
                    box-shadow: 0 2px 8px rgba(93, 78, 55, 0.3);
                    cursor: pointer;
                    user-select: none;
                    pointer-events: all;
                ">${table.number}</div>`,
                iconSize: [40, 40],
                iconAnchor: [20, 20]
            }),
            interactive: true,
            bubblingMouseEvents: false
        }).addTo(this.map);

        // Store markers
        this.tableMarkers[table.number] = {
            shape: tableMarker,
            label: labelMarker,
            table: table,
            coords: coords,
            size: size
        };

        // Setup interactions - ONLY on the label to prevent jumping
        this.setupTableInteractions(table.number, labelMarker);

        // Add guest avatars
        if (table.guest_list && table.guest_list.length > 0) {
            this.addGuestAvatars(table, coords, shape, size);
        }
    }

    setupTableInteractions(tableNumber, labelMarker) {
        const tableData = this.tableMarkers[tableNumber];
        
        // Click handler
        labelMarker.on('click', (e) => {
            e.originalEvent?.stopPropagation();
            this.handleTableClick(tableData.table);
        });

        // Mobile-friendly hover (tooltip only)
        if (window.innerWidth > 768) {
            labelMarker.on('mouseover', () => {
                this.showTableTooltip(tableNumber);
            });

            labelMarker.on('mouseout', () => {
                this.hideTableTooltip();
            });
        }

        // Popup for detailed info
        const popupContent = this.createTablePopup(tableData.table);
        labelMarker.bindPopup(popupContent, {
            maxWidth: window.innerWidth <= 768 ? 200 : 280,
            minWidth: window.innerWidth <= 768 ? 150 : 200,
            closeButton: true,
            autoClose: true,
            autoPan: true,
            autoPanPadding: [20, 20],
            className: 'table-popup',
            offset: [0, -10] // Slight offset to avoid covering the table marker
        });
    }

    showTableTooltip(tableNumber) {
        // Simple tooltip without CSS transforms that cause jumping
        const table = this.tableMarkers[tableNumber]?.table;
        if (!table) return;

        const tooltipDiv = document.createElement('div');
        tooltipDiv.id = 'table-tooltip';
        tooltipDiv.className = 'table-tooltip-simple';
        tooltipDiv.innerHTML = `
            <strong>Stół ${table.number}</strong><br>
            ${table.name}<br>
            <small>${table.guests_count}/${table.capacity} miejsc</small>
        `;
        tooltipDiv.style.cssText = `
            position: fixed;
            background: rgba(93, 78, 55, 0.95);
            color: #f5f0e8;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.9rem;
            z-index: 10000;
            pointer-events: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            max-width: 200px;
        `;

        document.body.appendChild(tooltipDiv);

        // Position tooltip
        document.addEventListener('mousemove', this.moveTooltip);
    }

    moveTooltip = (e) => {
        const tooltip = document.getElementById('table-tooltip');
        if (tooltip) {
            tooltip.style.left = (e.clientX + 15) + 'px';
            tooltip.style.top = (e.clientY - 15) + 'px';
        }
    }

    hideTableTooltip() {
        const tooltip = document.getElementById('table-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
        document.removeEventListener('mousemove', this.moveTooltip);
    }

    handleTableClick(table) {
        console.log(`🖱️ Table ${table.number} clicked`);
        
        this.clearHighlights();
        this.highlightTable(table.number);
        this.highlightTableCard(table.number);
        this.showNotification(`Wybrano stół ${table.number}: ${table.name}`, 'info');
    }

    highlightTable(tableNumber) {
        const tableData = this.tableMarkers[tableNumber];
        if (!tableData) return;

        this.clearHighlights();
        this.currentHighlighted = tableNumber;

        // Update colors
        const highlightColor = '#5d4e37';
        const highlightBorder = '#2c1810';

        tableData.shape.setStyle({
            fillColor: highlightColor,
            color: highlightBorder,
            weight: 4
        });

        // Update label
        const labelElement = tableData.label.getElement();
        if (labelElement) {
            const labelDiv = labelElement.querySelector('.table-number-label');
            if (labelDiv) {
                labelDiv.style.background = highlightColor;
                labelDiv.style.color = '#f5f0e8';
                labelDiv.style.borderColor = highlightBorder;
                labelDiv.style.transform = 'scale(1.1)';
            }
        }

        // Center on table
        this.map.panTo(tableData.coords, { animate: true, duration: 0.5 });
    }

    clearHighlights() {
        Object.values(this.tableMarkers).forEach(({ shape, label, table }) => {
            const defaultColor = table.color || '#d4c4a8';
            const defaultBorder = table.border_color || '#b8a082';

            shape.setStyle({
                fillColor: defaultColor,
                color: defaultBorder,
                weight: 3
            });

            // Reset label
            const labelElement = label.getElement();
            if (labelElement) {
                const labelDiv = labelElement.querySelector('.table-number-label');
                if (labelDiv) {
                    labelDiv.style.background = defaultColor;
                    labelDiv.style.color = '#5d4e37';
                    labelDiv.style.borderColor = defaultBorder;
                    labelDiv.style.transform = 'scale(1)';
                }
            }
        });

        this.currentHighlighted = null;
        this.clearCardHighlights();
    }

    addGuestAvatars(table, coords, shape, size) {
        if (!table.guest_list || table.guest_list.length === 0) return;

        const guests = table.guest_list;
        const totalGuests = guests.length;
        
        guests.forEach((guest, index) => {
            const isCurrent = this.currentGuestInfo && this.currentGuestInfo.id === guest.id;
            let avatarCoords;

            if (shape === 'rectangular' || shape === 'square') {
                avatarCoords = this.calculateRectangularAvatarPosition(coords, size, index, totalGuests);
            } else {
                avatarCoords = this.calculateCircularAvatarPosition(coords, index, totalGuests);
            }

            if (avatarCoords) {
                this.createGuestAvatar(guest, avatarCoords, isCurrent, table.number, index + 1);
            }
        });
    }

    calculateCircularAvatarPosition(center, index, total) {
        const radius = window.innerWidth <= 768 ? 35 : 45; // Responsive radius
        const angle = (360 / total) * index - 90; // Start from top
        const radian = (angle * Math.PI) / 180;
        
        return [
            center[0] + Math.sin(radian) * radius,
            center[1] + Math.cos(radian) * radius
        ];
    }

    calculateRectangularAvatarPosition(center, size, index, total) {
        const margin = 25; // Distance from table edge
        const [width, height] = size;
        
        let x, y;
        
        if (width > height) {
            // Horizontal table (wider than tall) - guests at top and bottom edges
            const spacing = width / (total + 1); // Evenly distribute with padding
            const offsetFromCenter = -width/2 + spacing * (index + 1);
            
            if (index % 2 === 0) {
                // Even indices - top edge
                x = center[0] - margin;
                y = center[1] + offsetFromCenter;
            } else {
                // Odd indices - bottom edge  
                x = center[0] + margin;
                y = center[1] + offsetFromCenter;
            }
        } else {
            // Vertical table (taller than wide) - guests only at left edge
            const spacing = height / (total + 1); // Evenly distribute with padding
            const offsetFromCenter = -height/2 + spacing * (index + 1);
            
            // All guests on left edge
            x = center[0] + offsetFromCenter;
            y = center[1] - margin;
        }
        
        return [x, y];
    }

    createGuestAvatar(guest, coords, isCurrent, tableNumber, seatNumber) {
        const isMobile = window.innerWidth <= 768;
        const avatarSize = isMobile ? (isCurrent ? 20 : 16) : (isCurrent ? 24 : 20);
        
        const avatarMarker = L.marker(coords, {
            icon: L.divIcon({
                className: 'guest-avatar-marker',
                html: `<div class="guest-avatar ${isCurrent ? 'current-guest' : ''}" style="
                    width: ${avatarSize}px; height: ${avatarSize}px;
                    border-radius: 50%;
                    background: linear-gradient(145deg, ${isCurrent ? '#d4a574, #b8935f' : '#8b6f47, #5d4e37'});
                    border: 2px solid #f5f0e8;
                    display: flex; align-items: center; justify-content: center;
                    font-size: ${avatarSize * 0.4}px; color: #f5f0e8; font-weight: bold;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                    cursor: pointer; user-select: none;
                ">${guest.user ? guest.user.first_name.charAt(0).toUpperCase() : guest.full_name.charAt(0).toUpperCase()}</div>`,
                iconSize: [avatarSize, avatarSize],
                iconAnchor: [avatarSize/2, avatarSize/2]
            }),
            interactive: true
        }).addTo(this.map);

        // Mobile-friendly interaction
        if (isMobile) {
            avatarMarker.on('click', (e) => {
                e.originalEvent?.stopPropagation();
                this.showGuestModal(guest, tableNumber, seatNumber);
            });
        } else {
            avatarMarker.on('click', (e) => {
                e.originalEvent?.stopPropagation();
                this.showGuestModal(guest, tableNumber, seatNumber);
            });

            avatarMarker.bindTooltip(`<strong>${guest.full_name}</strong><br>Stół ${tableNumber}, Miejsce ${seatNumber}`, {
                direction: 'top',
                offset: [0, -5]
            });
        }

        // Store guest marker
        if (!this.guestMarkers[tableNumber]) {
            this.guestMarkers[tableNumber] = [];
        }
        this.guestMarkers[tableNumber].push(avatarMarker);
    }

    createTablePopup(table) {
        const currentGuest = this.currentGuestInfo;
        const isMobile = window.innerWidth <= 768;
        let guestsHtml = '';
        
        if (table.guest_list && table.guest_list.length > 0) {
            const maxGuests = isMobile ? 4 : 6; // Limit guests shown on mobile
            const visibleGuests = table.guest_list.slice(0, maxGuests);
            const remainingCount = table.guest_list.length - maxGuests;
            
            guestsHtml = visibleGuests.map(guest => {
                const isCurrent = currentGuest && currentGuest.id === guest.id;
                return `<span class="guest-badge${isCurrent ? ' current' : ''}" style="
                    display: inline-block; background: ${isCurrent ? '#8b6f47' : '#d4c4a8'}; 
                    color: ${isCurrent ? '#f5f0e8' : '#5d4e37'}; padding: 1px 4px; 
                    border-radius: 8px; font-size: 0.65rem; margin: 1px;">${guest.full_name}</span>`;
            }).join('');
            
            if (remainingCount > 0) {
                guestsHtml += `<span style="font-size: 0.65rem; color: #8b6f47; margin-left: 4px;">+${remainingCount} więcej</span>`;
            }
        }

        return `
            <div class="table-popup" style="font-family: Georgia, serif; font-size: ${isMobile ? '0.8rem' : '0.9rem'};">
                <div style="font-weight: bold; color: #5d4e37; margin-bottom: 4px;">Stół ${table.number}</div>
                ${table.name ? `<div style="color: #8b6f47; font-weight: bold; margin-bottom: 3px; font-size: 0.85em;">${table.name}</div>` : ''}
                ${table.description ? `<div style="color: #6b5b4f; margin-bottom: 4px; font-size: 0.8em;">${table.description}</div>` : ''}
                <div style="color: #5d4e37; margin-bottom: 6px; font-size: 0.8em;">Zajętość: ${table.guests_count}/${table.capacity}</div>
                ${guestsHtml ? `<div style="margin-top: 6px; line-height: 1.2;">${guestsHtml}</div>` : ''}
            </div>
        `;
    }

    // Additional helper methods...
    setupSearch() {
        // Simplified search for now
        console.log('🔍 Search setup complete');
    }

    setupEventListeners() {
        // Handle window resize
        window.addEventListener('resize', () => {
            if (this.map) {
                setTimeout(() => {
                    this.map.invalidateSize();
                    this.handleResize();
                }, 100);
            }
        });

        // Close tooltips when clicking elsewhere
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.table-number-marker') && !e.target.closest('.guest-avatar-marker')) {
                this.hideTableTooltip();
            }
        });
    }

    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;
        
        // Recreate map if switching between mobile/desktop
        if (wasMobile !== this.isMobile) {
            console.log('📱 Device type changed, recreating map...');
            this.createMap();
            this.addTables();
        }
    }

    addTestTables() {
        console.log('🧪 Adding test tables...');
        // Fallback test tables with reasonable positions
        const testTables = [
            { number: 1, name: 'Test 1', map_x: 200, map_y: 150, map_width: 80, map_height: 80, shape: 'circular', capacity: 8, guests_count: 3, guest_list: [] },
            { number: 2, name: 'Test 2', map_x: 400, map_y: 150, map_width: 80, map_height: 80, shape: 'circular', capacity: 8, guests_count: 5, guest_list: [] },
            { number: 3, name: 'Test 3', map_x: 600, map_y: 150, map_width: 80, map_height: 80, shape: 'circular', capacity: 8, guests_count: 2, guest_list: [] }
        ];

        testTables.forEach(table => {
            this.createResponsiveTableMarker(table);
        });
    }

    highlightTableCard(tableNumber) {
        const card = document.querySelector(`[data-table-card="${tableNumber}"]`);
        if (card) {
            card.classList.add('highlighted-card');
            card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    clearCardHighlights() {
        document.querySelectorAll('.table-card').forEach(card => {
            card.classList.remove('highlighted-card');
        });
    }

    showGuestModal(guest, tableNumber, seatNumber) {
        console.log(`👤 Showing guest modal: ${guest.full_name}`);
        
        // Remove any existing guest info
        const existingInfo = document.getElementById('guest-info-display');
        if (existingInfo) {
            existingInfo.remove();
        }

        // Create a simple info box below the map
        const guestInfo = document.createElement('div');
        guestInfo.id = 'guest-info-display';
        guestInfo.style.cssText = `
            background: linear-gradient(135deg, #f8f5f0, #ede8dd);
            border: 2px solid #d4c4a8;
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(93, 78, 55, 0.2);
            font-family: Georgia, serif;
            color: #5d4e37;
        `;
        
        guestInfo.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h5 style="margin: 0; color: #5d4e37;">👤 Informacje o gościu</h5>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none; border: none; font-size: 1.2rem; cursor: pointer; 
                    color: #8b6f47; padding: 0; line-height: 1;">×</button>
            </div>
            <div style="display: grid; grid-template-columns: auto 1fr; gap: 10px; align-items: center;">
                <strong>Imię:</strong> <span>${guest.full_name}</span>
                <strong>Stół:</strong> <span>${tableNumber}</span>
                <strong>Miejsce:</strong> <span>${seatNumber}</span>
                ${guest.dietary_requirements ? `<strong>Dieta:</strong> <span>${guest.dietary_requirements}</span>` : ''}
            </div>
        `;

        // Insert after the map container
        const mapContainer = document.querySelector('.table-map-container');
        if (mapContainer) {
            mapContainer.parentNode.insertBefore(guestInfo, mapContainer.nextSibling);
            
            // Smooth scroll to the info
            guestInfo.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    showNotification(message, type = 'info') {
        console.log(`📢 ${type.toUpperCase()}: ${message}`);
        
        // Simple notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 250px; max-width: 90vw;';
        notification.innerHTML = `${message} <button type="button" class="close" onclick="this.parentElement.remove()"><span>&times;</span></button>`;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 4000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌟 DOM loaded, initializing wedding table map...');
    
    if (document.getElementById('wedding-map')) {
        window.weddingTableMap = new WeddingTableMap();
    } else {
        console.error('❌ Map container not found!');
    }
});