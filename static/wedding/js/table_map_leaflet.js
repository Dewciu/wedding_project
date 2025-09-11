// Wedding Table Map - Leaflet Version

class WeddingTableMap {
    constructor() {
        this.map = null;
        this.tableMarkers = {};
        this.guestMarkers = {};
        this.currentHighlighted = null;
        this.searchTimeout = null;
        this.currentGuestInfo = window.weddingData?.currentGuestInfo || null;
        this.mapBounds = { width: 900, height: 600 }; // Virtual coordinates
        
        // Mobile responsiveness
        this.isMobile = window.innerWidth <= 768;
        this.isSmallMobile = window.innerWidth <= 480;
        this.mobileScale = 1.0; // Will be set in createMap()
        this.minGuestZoom = -0.5; // Will be adjusted in createMap()
        
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
        const isMobile = window.innerWidth <= 768;
        const isSmallMobile = window.innerWidth <= 480;
        
        // Clear any existing map
        if (this.map) {
            this.map.remove();
        }

        // Calculate responsive scaling factors
        this.mobileScale = isMobile ? (isSmallMobile ? 0.6 : 0.75) : 1.0;
        this.minGuestZoom = isMobile ? -3 : -2; // Lowered thresholds to make guests always visible
        
        this.map = L.map('wedding-map', {
            crs: L.CRS.Simple,
            minZoom: isMobile ? -2.5 : -1.5,
            maxZoom: isMobile ? 1.5 : 2.5,
            zoomControl: true,
            attributionControl: false,
            scrollWheelZoom: !isMobile,
            doubleClickZoom: true,
            touchZoom: isMobile,
            dragging: true,
            tap: isMobile,
            tapTolerance: isMobile ? 20 : 10,
            renderer: L.canvas({ padding: 0.5 })
        });

        // Set bounds based on our virtual coordinate system with responsive scaling
        const scaledWidth = this.mapBounds.width * this.mobileScale;
        const scaledHeight = this.mapBounds.height * this.mobileScale;
        const bounds = [[0, 0], [scaledHeight, scaledWidth]];
        
        this.map.fitBounds(bounds);
        this.map.setMaxBounds([[-50, -50], [scaledHeight + 50, scaledWidth + 50]]);

        // Custom zoom control positioning
        this.map.zoomControl.setPosition('topright');

        // Add venue background
        this.addVenueBackground();
        
        // Mobile-specific optimizations
        if (isMobile) {
            this.setupMobileOptimizations();
        }

        // Listen for zoom changes to hide/show guests
        this.map.on('zoomend', () => {
            this.handleZoomChange();
        });
    }

    addVenueBackground() {
        // Venue outline with responsive scaling
        const scaledWidth = this.mapBounds.width * this.mobileScale;
        const scaledHeight = this.mapBounds.height * this.mobileScale;
        
        const venueOutline = L.rectangle([
            [50 * this.mobileScale, 50 * this.mobileScale], 
            [scaledHeight - 50 * this.mobileScale, scaledWidth - 50 * this.mobileScale]
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
        const tables = window.weddingData?.tables || [];
        
        if (tables.length === 0) {
            this.addTestTables();
            return;
        }
        
        tables.forEach(table => {
            try {
                this.createResponsiveTableMarker(table);
            } catch (error) {
                console.error(`Error creating table ${table.number}:`, error);
            }
        });
    }

    createResponsiveTableMarker(table) {
        // Use database coordinates with responsive scaling
        const baseX = parseFloat(table.map_x) || 450;
        const baseY = parseFloat(table.map_y) || 300;
        const baseWidth = parseFloat(table.map_width) || 85;
        const baseHeight = parseFloat(table.map_height) || 85;
        
        // Apply mobile scaling
        const x = baseX * this.mobileScale;
        const y = baseY * this.mobileScale;
        const width = baseWidth * this.mobileScale;
        const height = baseHeight * this.mobileScale;
        
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

        // Create table shape with responsive sizing
        if (shape === 'rectangular' || shape === 'square') {
            const bounds = [
                [y - height/2, x - width/2],
                [y + height/2, x + width/2]
            ];
            
            tableMarker = L.rectangle(bounds, {
                color: strokeColor,
                fillColor: fillColor,
                fillOpacity: 0.8,
                weight: Math.max(2, 3 * this.mobileScale),
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
                weight: Math.max(2, 3 * this.mobileScale),
                interactive: true,
                bubblingMouseEvents: false,
                className: 'table-shape'
            }).addTo(this.map);
        }

        // Create table number label with responsive sizing
        const labelSize = Math.max(30, 40 * this.mobileScale);
        const fontSize = Math.max(0.9, 1.2 * this.mobileScale);
        
        const labelMarker = L.marker(coords, {
            icon: L.divIcon({
                className: 'table-number-marker',
                html: `<div class="table-number-label" style="
                    background: ${fillColor}; 
                    color: ${isHighlighted ? '#f5f0e8' : '#5d4e37'}; 
                    border: 2px solid ${strokeColor}; 
                    border-radius: ${shape === 'circular' ? '50%' : '6px'};
                    width: ${labelSize}px; height: ${labelSize}px;
                    display: flex; align-items: center; justify-content: center;
                    font-weight: bold; font-size: ${fontSize}rem;
                    box-shadow: 0 2px 8px rgba(93, 78, 55, 0.3);
                    cursor: pointer;
                    user-select: none;
                    pointer-events: all;
                ">${table.number}</div>`,
                iconSize: [labelSize, labelSize],
                iconAnchor: [labelSize/2, labelSize/2]
            }),
            interactive: true,
            bubblingMouseEvents: false
        }).addTo(this.map);

        // Store markers with scaled coordinates
        this.tableMarkers[table.number] = {
            shape: tableMarker,
            label: labelMarker,
            table: table,
            coords: coords,
            size: size,
            baseCoords: [baseY, baseX], // Store original coordinates
            baseSize: [baseWidth, baseHeight]
        };

        // Setup interactions - ONLY on the label to prevent jumping
        this.setupTableInteractions(table.number, labelMarker);

        // Add guest avatars if zoom level allows
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
        this.clearHighlights();
        this.highlightTable(table.number);
        
        // Small delay before scrolling to allow user to see map highlight first
        setTimeout(() => {
            this.highlightTableCard(table.number);
        }, 300);
        
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
        if (!table.guest_list || table.guest_list.length === 0) {
            return;
        }

        const guests = table.guest_list;
        const totalGuests = guests.length;
        
        // Use the passed coords directly - they are already correctly calculated and scaled
        const actualCenter = coords;
        
        // Sort guests by chair_position if available, otherwise use array order
        const sortedGuests = [...guests].sort((a, b) => {
            const posA = a.chair_position || 0;
            const posB = b.chair_position || 0;
            
            // If both have positions, sort by position
            if (posA > 0 && posB > 0) {
                return posA - posB;
            }
            // If only one has position, put positioned guests first
            if (posA > 0) return -1;
            if (posB > 0) return 1;
            // If neither has position, maintain original order
            return guests.indexOf(a) - guests.indexOf(b);
        });
        
        sortedGuests.forEach((guest, sortedIndex) => {
            const isCurrent = this.currentGuestInfo && this.currentGuestInfo.id === guest.id;
            let avatarCoords;
            
            // Use chair_position if available, otherwise use sorted index
            const effectivePosition = guest.chair_position || (sortedIndex + 1);
            const positionIndex = effectivePosition - 1; // Convert to 0-based index

            if (shape === 'rectangular' || shape === 'square') {
                avatarCoords = this.calculateRectangularAvatarPosition(actualCenter, size, positionIndex, totalGuests);
            } else {
                avatarCoords = this.calculateCircularAvatarPosition(actualCenter, positionIndex, totalGuests);
            }

            if (avatarCoords) {
                const avatar = this.createGuestAvatar(guest, avatarCoords, isCurrent, table.number, effectivePosition);
            }
        });
    }

    calculateCircularAvatarPosition(center, index, total) {
        // Responsive radius based on current scale and zoom - smaller for less spacing
        const baseRadius = 65; // Reduced from 85 to 65 for closer positioning
        const scaledRadius = baseRadius * this.mobileScale;
        const currentZoom = this.map ? this.map.getZoom() : 0;
        const zoomFactor = Math.max(0.6, Math.min(2.0, currentZoom + 1.2)); // More generous zoom scaling
        const radius = scaledRadius * zoomFactor;
        
        const angle = (360 / total) * index - 90; // Start from top
        const radian = (angle * Math.PI) / 180;
        
        const result = [
            center[0] + Math.sin(radian) * radius,
            center[1] + Math.cos(radian) * radius
        ];
        
        return result;
    }

    calculateRectangularAvatarPosition(center, size, index, total) {
        // Responsive margin based on scale - smaller for closer positioning
        const baseMargin = 40; // Reduced from 50 to 40 for closer positioning
        const margin = baseMargin * this.mobileScale;
        const [width, height] = size;
        
        let x, y;
        
        if (width > height) {
            // Horizontal table (wider than tall) - guests at top and bottom edges
            const spacing = width / (total + 1); // Evenly distribute with padding
            const offsetFromCenter = -width/2 + spacing * (index + 1);
            
            if (index % 2 === 0) {
                // Even indices - top edge (above center)
                x = center[0] - margin; // Move up (negative Y direction in Leaflet)
                y = center[1] + offsetFromCenter; // Along width
            } else {
                // Odd indices - bottom edge (below center)
                x = center[0] + margin; // Move down (positive Y direction in Leaflet)
                y = center[1] + offsetFromCenter; // Along width
            }
        } else {
            // Vertical table (taller than wide) - guests only at left edge
            const spacing = height / (total + 1); // Evenly distribute with padding
            const offsetFromCenter = -height/2 + spacing * (index + 1);
            
            // All guests on left edge
            x = center[0] + offsetFromCenter; // Along height
            y = center[1] - margin; // Move left (negative X direction in Leaflet)
        }
        
        return [x, y];
    }

    createGuestAvatar(guest, coords, isCurrent, tableNumber, seatNumber) {
        const isMobile = window.innerWidth <= 768;
        const currentZoom = this.map ? this.map.getZoom() : 0;
        
        // Guests are always visible now - no zoom restrictions
        
        // Responsive avatar size based on device and zoom - smaller for less clutter
        const baseSize = isCurrent ? 30 : 28; // Reduced from 36:32 to 28:24
        const scaledSize = Math.max(26, baseSize * this.mobileScale); // Reduced minimum from 20 to 16
        const zoomFactor = Math.max(0.8, Math.min(2.5, currentZoom + 1.5)); // More generous zoom scaling
        const avatarSize = Math.round(scaledSize * zoomFactor);
        
        const avatarMarker = L.marker(coords, {
            icon: L.divIcon({
                className: 'guest-avatar-marker',
                html: `<div class="guest-avatar ${isCurrent ? 'current-guest' : ''}" 
                    data-guest-id="${guest.id}" 
                    data-table-number="${tableNumber}" 
                    data-seat-number="${seatNumber}"
                    style="
                        width: ${avatarSize}px; height: ${avatarSize}px;
                        border-radius: 50%;
                        background: linear-gradient(145deg, ${isCurrent ? '#d4a574, #b8935f' : '#8b6f47, #5d4e37'});
                        border: 2px solid #f5f0e8;
                        display: flex; align-items: center; justify-content: center;
                        font-size: ${avatarSize * 0.4}px; color: #f5f0e8; font-weight: bold;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                        cursor: grab; user-select: none;
                        transition: opacity 0.3s ease, transform 0.2s ease;
                    ">${guest.user ? guest.user.first_name.charAt(0).toUpperCase() : guest.full_name.charAt(0).toUpperCase()}</div>`,
                iconSize: [avatarSize, avatarSize],
                iconAnchor: [avatarSize/2, avatarSize/2]
            }),
            interactive: true,
            zIndexOffset: isCurrent ? 1000 : 100
        }).addTo(this.map);

        // Click interaction for guest modal
        avatarMarker.on('click', (e) => {
            e.originalEvent?.stopPropagation();
            this.showGuestModal(guest, tableNumber, seatNumber);
        });

        if (!isMobile) {
            avatarMarker.bindTooltip(`<strong>${guest.full_name}</strong><br>Stół ${tableNumber}, Miejsce ${seatNumber}`, {
                direction: 'top',
                offset: [0, -5]
            });
        }

        // Store guest marker for zoom management
        if (!this.guestMarkers[tableNumber]) {
            this.guestMarkers[tableNumber] = [];
        }
        this.guestMarkers[tableNumber].push(avatarMarker);
        
        return avatarMarker;
    }

    getCSRFToken() {
        // Get CSRF token from cookie or meta tag
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenElement) {
            return tokenElement.value;
        }
        
        // Try to get from cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        return '';
    }

    // ...existing code...
    setupSearch() {
        const searchForm = document.getElementById('table-search-form');
        const searchInput = searchForm?.querySelector('input[name="search_query"]');
        
        if (!searchForm || !searchInput) {
            return;
        }
        
        // USUNIĘTE: Real-time search as user types - teraz tylko po kliknięciu/submit
        
        // Handle form submission - GŁÓWNY SPOSÓB WYSZUKIWANIA
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query.length >= 2) {
                this.performSearch(query);
            } else {
                this.showNotification('Wpisz przynajmniej 2 znaki imienia i nazwiska', 'info');
            }
        });
        
        // Dodaj obsługę dla przycisku Enter
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = searchInput.value.trim();
                if (query.length >= 2) {
                    this.performSearch(query);
                } else {
                    this.showNotification('Wpisz przynajmniej 2 znaki imienia i nazwiska', 'info');
                }
            }
        });
        
        console.log('✅ Search functionality setup complete - search on submit only');
    }

    performSearch(query) {
        console.log(`🔍 Searching for: "${query}"`);
        
        // AJAX search
        fetch(`/ajax/table-search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.found) {
                    this.handleSearchSuccess(data);
                } else {
                    this.handleSearchNoResults(query);
                }
            })
            .catch(error => {
                console.error('❌ Search error:', error);
                this.showNotification('Wystąpił błąd podczas wyszukiwania', 'error');
            });
    }

    handleSearchSuccess(data) {
        console.log(`✅ Guest found:`, data);
        
        // Clear previous highlights
        this.clearSearchHighlights();
        
        if (!data.table_number || data.table_number === 'Nie przypisano') {
            this.showNotification(`Znaleziono: ${data.guest_name} - Brak przypisanego stołu`, 'warning');
            return;
        }
        
        // Find table marker
        const tableData = this.tableMarkers[data.table_number];
        if (!tableData) {
            this.showNotification(`Znaleziono: ${data.guest_name} - Stół ${data.table_number} (nie znaleziono na mapie)`, 'warning');
            return;
        }
        
        // Highlight table on map
        this.highlightTable(data.table_number);
        
        // Zoom and pan to table with smooth animation
        this.map.setView(tableData.coords, 1, { 
            animate: true,
            duration: 1.0
        });
        
        // Highlight specific guest avatar after zoom
        setTimeout(() => {
            this.highlightGuestAvatar(data.guest_id, data.table_number);
        }, 600);
        
        // Highlight table card after a delay
        setTimeout(() => {
            this.highlightTableCard(data.table_number);
        }, 500);
        
        // Show success notification
        const tableName = data.table_name ? ` (${data.table_name})` : '';
        this.showNotification(`Znaleziono: ${data.guest_name} - Stół ${data.table_number}${tableName}`, 'success');
    }

    handleSearchNoResults(query) {
        console.log(`❌ No results for: "${query}"`);
        this.clearSearchHighlights();
        this.showNotification(`Nie znaleziono gościa: "${query}"`, 'info');
    }

    highlightGuestAvatar(guestId, tableNumber) {
        console.log(`👤 Highlighting guest avatar: ID ${guestId} at table ${tableNumber}`);
        
        // Clear any existing guest highlights
        this.clearGuestHighlights();
        
        // Find the guest markers for this table
        const tableGuests = this.guestMarkers[tableNumber];
        if (!tableGuests || !Array.isArray(tableGuests)) {
            console.log(`❌ No guest markers found for table ${tableNumber}`);
            return;
        }
        
        // Find the specific guest avatar
        let targetAvatar = null;
        tableGuests.forEach(guestMarker => {
            if (guestMarker && guestMarker.getElement) {
                const element = guestMarker.getElement();
                const avatarDiv = element?.querySelector('.guest-avatar');
                if (avatarDiv) {
                    // Check if this avatar matches our target guest
                    // The guest ID should be stored in a data attribute
                    const avatarGuestId = avatarDiv.dataset.guestId;
                    if (avatarGuestId && parseInt(avatarGuestId) === parseInt(guestId)) {
                        targetAvatar = avatarDiv;
                        console.log(`✅ Found target guest avatar for ID ${guestId}`);
                        return;
                    }
                }
            }
        });
        
        if (targetAvatar) {
            // Add visual highlight to the avatar
            targetAvatar.classList.add('search-highlighted');
            targetAvatar.style.animation = 'search-pulse 2s infinite';
            targetAvatar.style.transform = 'scale(1.3)';
            targetAvatar.style.zIndex = '9999';
            targetAvatar.style.boxShadow = '0 0 20px rgba(212, 165, 116, 0.8), 0 0 40px rgba(212, 165, 116, 0.4)';
            
            console.log(`✨ Guest avatar highlighted for ID ${guestId}`);
            
            // Remove highlight after a few seconds
            setTimeout(() => {
                if (targetAvatar && targetAvatar.parentNode) {
                    targetAvatar.style.animation = '';
                    targetAvatar.style.transform = '';
                    targetAvatar.style.zIndex = '';
                    targetAvatar.style.boxShadow = '';
                    targetAvatar.classList.remove('search-highlighted');
                }
            }, 4000);
        } else {
            console.log(`❌ Could not find guest avatar for ID ${guestId} at table ${tableNumber}`);
        }
    }
    
    clearGuestHighlights() {
        // Clear all guest avatar highlights
        document.querySelectorAll('.guest-avatar.search-highlighted').forEach(avatar => {
            avatar.classList.remove('search-highlighted');
            avatar.style.animation = '';
            avatar.style.transform = '';
            avatar.style.zIndex = '';
            avatar.style.boxShadow = '';
        });
    }

    clearSearchHighlights() {
        // Clear table highlights
        this.clearHighlights();
        this.clearCardHighlights();
        // Clear guest highlights
        this.clearGuestHighlights();
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
        const wasSmallMobile = this.isSmallMobile;
        
        this.isMobile = window.innerWidth <= 768;
        this.isSmallMobile = window.innerWidth <= 480;
        
        // Update mobile scale
        const newScale = this.isMobile ? (this.isSmallMobile ? 0.6 : 0.75) : 1.0;
        const scaleChanged = Math.abs(newScale - this.mobileScale) > 0.05;
        
        // Recreate map if significant changes occurred
        if (wasMobile !== this.isMobile || wasSmallMobile !== this.isSmallMobile || scaleChanged) {
            console.log('📱 Device layout changed significantly, recreating map...', {
                wasMobile, 'isMobile': this.isMobile,
                wasSmallMobile, 'isSmallMobile': this.isSmallMobile,
                'oldScale': this.mobileScale, 'newScale': newScale
            });
            
            this.mobileScale = newScale;
            this.createMap();
            this.addTables();
        } else {
            // Just invalidate size for minor changes
            this.map.invalidateSize();
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
        if (!card) {
            console.log(`⚠️ Table card ${tableNumber} not found in DOM`);
            return;
        }
        
        // Clear previous highlights
        this.clearCardHighlights();
        
        // Add highlight class
        card.classList.add('highlighted-card');
        
        // Scroll to center with smooth animation
        card.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center',
            inline: 'nearest'
        });
        
        // Add temporary glow effect
        card.style.transition = 'all 0.3s ease';
        card.style.boxShadow = '0 8px 25px rgba(139, 111, 71, 0.4), 0 0 0 3px rgba(139, 111, 71, 0.2)';
        card.style.transform = 'scale(1.02)';
        
        // Remove glow after animation
        setTimeout(() => {
            if (card && card.parentNode) {
                card.style.boxShadow = '';
                card.style.transform = '';
            }
        }, 2000);
        
        console.log(`✨ Table card ${tableNumber} highlighted and scrolled to center`);
    }

    clearCardHighlights() {
        document.querySelectorAll('.table-card').forEach(card => {
            card.classList.remove('highlighted-card');
            // Reset any inline styles from temporary highlighting
            card.style.boxShadow = '';
            card.style.transform = '';
            card.style.transition = '';
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
        
        const isMobile = window.innerWidth <= 768;
        const dragInstruction = isMobile ? 
            'Przytrzymaj i przeciągnij avatar aby zmienić miejsce' : 
            'Przeciągnij avatar na mapie aby zmienić miejsce przy stole';
        
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
            <div style="margin-top: 15px; padding: 10px; background: rgba(212, 196, 168, 0.3); border-radius: 6px; border-left: 4px solid #d4c4a8;">
                <small style="color: #5d4e37; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-hand-paper" style="color: #8b6f47;"></i>
                    <strong>Wskazówka:</strong> ${dragInstruction}
                </small>
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

    handleZoomChange() {
        if (!this.map) return;
        
        const currentZoom = this.map.getZoom();
        console.log(`🔍 Zoom changed to: ${currentZoom}, minGuestZoom: ${this.minGuestZoom}`);
        
        // Show/hide guest avatars based on zoom level
        Object.keys(this.guestMarkers).forEach(tableNumber => {
            const markers = this.guestMarkers[tableNumber];
            if (markers && markers.length > 0) {
                markers.forEach(marker => {
                    const element = marker.getElement();
                    if (element) {
                        const avatar = element.querySelector('.guest-avatar');
                        if (avatar) {
                            if (currentZoom >= this.minGuestZoom) {
                                avatar.style.opacity = '1';
                                avatar.style.pointerEvents = 'all';
                                marker.setZIndexOffset(marker.options.zIndexOffset);
                            } else {
                                avatar.style.opacity = '0.3';
                                avatar.style.pointerEvents = 'none';
                                marker.setZIndexOffset(-1000);
                            }
                        }
                    }
                });
            }
        });
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

    createTablePopup(table) {
        const guestCount = table.guest_list ? table.guest_list.length : 0;
        const availableSeats = table.capacity - guestCount;
        
        return `
            <div class="table-popup-content">
                <h4 style="margin: 0 0 10px 0; color: #5d4e37; font-size: 1.1rem;">
                    ${table.name || `Stół ${table.number}`}
                </h4>
                <div style="display: grid; gap: 5px; font-size: 0.9rem;">
                    <div><strong>Numer:</strong> ${table.number}</div>
                    <div><strong>Miejsca:</strong> ${table.capacity}</div>
                    <div><strong>Wolne:</strong> ${availableSeats}</div>
                    ${table.description ? `<div><strong>Opis:</strong> ${table.description}</div>` : ''}
                </div>
                ${guestCount > 0 ? `
                    <div style="margin-top: 10px;">
                        <strong>Goście:</strong>
                        <div style="max-height: 120px; overflow-y: auto; margin-top: 5px; font-size: 0.8rem;">
                            ${table.guest_list.slice(0, 10).map(guest => `
                                <div style="padding: 2px 0;">${guest.full_name}${guest.chair_position ? ` (miejsce ${guest.chair_position})` : ''}</div>
                            `).join('')}
                            ${table.guest_list.length > 10 ? `<div style="padding: 2px 0; font-style: italic;">...i ${table.guest_list.length - 10} więcej</div>` : ''}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌟 DOM loaded, initializing wedding table map...');
    
    if (document.getElementById('wedding-map')) {
        console.log('✅ Map container found, creating map...');
        window.weddingTableMap = new WeddingTableMap();
    } else {
        console.error('❌ Map container not found!');
    }
});