// Wedding Table Map with Leaflet.js
class WeddingTableMap {
    constructor() {
        this.map = null;
        this.tableMarkers = {};
        this.guestMarkers = {};
        this.currentHighlighted = null;
        this.searchTimeout = null;
        this.currentGuestInfo = window.weddingData?.currentGuestInfo || null;
        
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
        // Detect if mobile device
        const isMobile = window.innerWidth <= 768;
        
        // Create map without default controls for cleaner look
        this.map = L.map('wedding-map', {
            crs: L.CRS.Simple,
            minZoom: isMobile ? -2 : -1,
            maxZoom: isMobile ? 1 : 2,
            zoomControl: false,
            attributionControl: false,
            scrollWheelZoom: !isMobile, // Disable scroll zoom on mobile to prevent conflicts
            doubleClickZoom: true,
            touchZoom: isMobile,
            dragging: true,
            tap: isMobile,
            tapTolerance: 15 // Better touch tolerance
        });

        // Define bounds for our venue layout
        const bounds = [[0, 0], [600, 900]];
        this.map.fitBounds(bounds);
        this.map.setMaxBounds(bounds.map(bound => [bound[0] - 50, bound[1] - 50]));

        // Add custom zoom controls with wedding styling
        const zoomControl = L.control.zoom({
            position: 'topright'
        });
        zoomControl.addTo(this.map);

        // Mobile-specific optimizations
        if (isMobile) {
            // Disable zoom on small touches to prevent accidental zooming
            this.map.on('touchstart', (e) => {
                if (e.originalEvent.touches.length > 1) {
                    this.map.touchZoom.disable();
                    setTimeout(() => {
                        if (this.map.touchZoom) {
                            this.map.touchZoom.enable();
                        }
                    }, 100);
                }
            });

            // Add loading indicator
            const mapElement = document.getElementById('wedding-map');
            mapElement.classList.add('loading');
            
            setTimeout(() => {
                mapElement.classList.remove('loading');
            }, 1500);
        }

        // Custom styling for zoom buttons
        setTimeout(() => {
            const zoomIn = document.querySelector('.leaflet-control-zoom-in');
            const zoomOut = document.querySelector('.leaflet-control-zoom-out');
            
            if (zoomIn && zoomOut) {
                [zoomIn, zoomOut].forEach(btn => {
                    btn.style.background = 'linear-gradient(145deg, #d4c4a8, #c8b99c)';
                    btn.style.border = '2px solid #b8a082';
                    btn.style.color = '#5d4e37';
                    btn.style.borderRadius = '8px';
                    btn.style.margin = '2px';
                    btn.style.boxShadow = '0 2px 6px rgba(93, 78, 55, 0.2)';
                    
                    // Better touch handling
                    if (isMobile) {
                        btn.addEventListener('touchstart', (e) => {
                            e.preventDefault();
                            btn.style.transform = 'scale(0.95)';
                        });
                        
                        btn.addEventListener('touchend', (e) => {
                            btn.style.transform = 'scale(1)';
                        });
                    }
                });
            }
        }, 100);

        // Add background pattern
        this.addBackgroundPattern();
    }

    addBackgroundPattern() {
        // Add a subtle background pattern to represent the venue
        const venueBackground = L.rectangle([[50, 100], [550, 800]], {
            color: 'transparent',
            fillColor: '#f8f5f0',
            fillOpacity: 0.3,
            weight: 0
        }).addTo(this.map);

        // Add decorative elements to represent venue layout
        const danceFloor = L.circle([300, 450], {
            radius: 80,
            color: '#d4c4a8',
            fillColor: '#ede8dd',
            fillOpacity: 0.5,
            weight: 2,
            dashArray: '5, 5'
        }).addTo(this.map);

        danceFloor.bindTooltip('<div class="table-popup"><div class="popup-title">🕺 Parkiet Taneczny</div><div class="popup-info">Miejsce na tańce i zabawę</div></div>', {
            permanent: false,
            direction: 'top'
        });
    }

    addTables() {
        const tables = window.weddingData?.tables || [];
        
        // Table positions (matching previous layout but adapted for Leaflet coordinates)
        const tablePositions = {
            1: { coords: [200, 170], size: [65, 200], type: 'rectangular' },  // Left vertical rectangle
            2: { coords: [520, 250], size: [500, 65], type: 'rectangular' },  // Bottom horizontal rectangle
            3: { coords: [80, 650], size: [600, 65], type: 'rectangular' },   // Top horizontal rectangle
            4: { coords: [180, 320], size: [85, 85], type: 'circular' },      // Chess pattern - top row
            5: { coords: [330, 430], size: [85, 85], type: 'circular' },      // Chess pattern - bottom row (offset)
            6: { coords: [360, 320], size: [85, 85], type: 'circular' },      // Chess pattern - top row
            7: { coords: [510, 430], size: [85, 85], type: 'circular' },      // Chess pattern - bottom row (offset)
            8: { coords: [540, 320], size: [85, 85], type: 'circular' },      // Chess pattern - top row
            9: { coords: [690, 430], size: [85, 85], type: 'circular' },      // Chess pattern - bottom row (offset)
            10: { coords: [720, 320], size: [85, 85], type: 'circular' }      // Chess pattern - top row
        };

        tables.forEach(table => {
            const position = tablePositions[table.number];
            if (!position) return;

            this.createTableMarker(table, position);
        });
    }

    createTableMarker(table, position) {
        const { coords, size, type, color, border_color } = position;
        const isHighlighted = this.currentGuestInfo && this.currentGuestInfo.table_number === table.number;
        
        // Use colors from database or defaults for highlighting
        const fillColor = isHighlighted ? '#5d4e37' : (color || '#d4c4a8');
        const strokeColor = isHighlighted ? '#2c1810' : (border_color || '#b8a082');
        
        let marker;
        
        if (type === 'rectangular' || type === 'square') {
            // Create rectangular table
            const bounds = [
                [coords[0] - size[1]/2, coords[1] - size[0]/2],
                [coords[0] + size[1]/2, coords[1] + size[0]/2]
            ];
            
            marker = L.rectangle(bounds, {
                color: strokeColor,
                fillColor: fillColor,
                fillOpacity: 0.8,
                weight: 3,
                className: `table-marker rectangular${isHighlighted ? ' highlighted' : ''}`
            }).addTo(this.map);
            
            // Add table number label for rectangles
            const labelMarker = L.marker(coords, {
                icon: L.divIcon({
                    className: 'table-number-label',
                    html: `<div style="background: ${fillColor}; color: ${isHighlighted ? '#f5f0e8' : '#5d4e37'}; border: 3px solid ${strokeColor}; border-radius: 8px; padding: 8px 12px; font-weight: bold; font-size: 1.2rem; box-shadow: 0 4px 15px rgba(93, 78, 55, 0.3); text-align: center; min-width: 40px;">${table.number}</div>`,
                    iconSize: [50, 30],
                    iconAnchor: [25, 15]
                })
            }).addTo(this.map);
            
            // Store both markers
            this.tableMarkers[table.number] = { shape: marker, label: labelMarker, table: table };
            
        } else {
            // Create circular table marker
            marker = L.circle(coords, {
                radius: Math.max(size[0], size[1]) / 2, // Use larger dimension for radius
                color: strokeColor,
                fillColor: fillColor,
                fillOpacity: 0.8,
                weight: 3,
                className: `table-marker${isHighlighted ? ' highlighted' : ''}`
            }).addTo(this.map);
            
            // Add table number label
            const labelMarker = L.marker(coords, {
                icon: L.divIcon({
                    className: 'table-number-label',
                    html: `<div style="background: ${isHighlighted ? '#5d4e37' : 'transparent'}; color: ${isHighlighted ? '#f5f0e8' : '#5d4e37'}; font-weight: bold; font-size: 1.4rem; text-shadow: 0 1px 2px rgba(255,255,255,0.5); text-align: center; line-height: 1;">${table.number}</div>`,
                    iconSize: [30, 30],
                    iconAnchor: [15, 15]
                })
            }).addTo(this.map);
            
            this.tableMarkers[table.number] = { shape: marker, label: labelMarker, table: table };
        }

        // Add click event for table
        marker.on('click', () => this.handleTableClick(table));
        if (this.tableMarkers[table.number].label) {
            this.tableMarkers[table.number].label.on('click', () => this.handleTableClick(table));
        }

        // Add popup with table information
        const popupContent = this.createTablePopup(table);
        marker.bindPopup(popupContent, {
            maxWidth: 250,
            className: 'table-popup-container'
        });

        // Add guest avatars around the table
        this.addGuestAvatars(table, coords, type, size);
    }

    createTablePopup(table) {
        const currentGuest = this.currentGuestInfo;
        let guestsHtml = '';
        
        if (table.guest_list && table.guest_list.length > 0) {
            guestsHtml = table.guest_list.map(guest => {
                const isCurrent = currentGuest && currentGuest.id === guest.id;
                return `<span class="guest-badge${isCurrent ? ' current' : ''}">${guest.full_name}</span>`;
            }).join('');
        }

        return `
            <div class="table-popup">
                <div class="popup-title">Stół ${table.number}</div>
                <div class="popup-info"><strong>${table.name}</strong></div>
                <div class="popup-info">${table.description}</div>
                <div class="popup-info">Zajętość: ${table.guests_count}/${table.capacity} miejsc</div>
                ${guestsHtml ? `<div class="guest-list">${guestsHtml}</div>` : ''}
            </div>
        `;
    }

    addGuestAvatars(table, coords, type, size) {
        if (!table.guest_list || table.guest_list.length === 0) return;

        const guests = table.guest_list;
        const totalGuests = guests.length;
        
        guests.forEach((guest, index) => {
            const isCurrent = this.currentGuestInfo && this.currentGuestInfo.id === guest.id;
            let avatarCoords;

            if (type === 'rectangular') {
                avatarCoords = this.calculateRectangularAvatarPosition(coords, size, index, totalGuests, table.number);
            } else {
                avatarCoords = this.calculateCircularAvatarPosition(coords, index, totalGuests);
            }

            if (avatarCoords) {
                this.createGuestAvatar(guest, avatarCoords, isCurrent, table.number, index + 1);
            }
        });
    }

    calculateCircularAvatarPosition(center, index, total) {
        const radius = 55; // Distance from table center
        const angle = (360 / total) * index - 90; // Start from top
        const radian = (angle * Math.PI) / 180;
        
        return [
            center[0] + Math.sin(radian) * radius,
            center[1] + Math.cos(radian) * radius
        ];
    }

    calculateRectangularAvatarPosition(center, size, index, total, tableNumber) {
        let x, y;
        
        if (tableNumber === 1) {
            // Vertical rectangle - position guests on the left side
            const spacing = size[1] / (total + 1);
            x = center[0];
            y = center[1] - size[0]/2 - 40; // To the left of the table
            x += -60; // Move further left
            y = center[0] - size[1]/2 + spacing * (index + 1); // Vertically distributed
        } else {
            // Horizontal rectangles (tables 2 & 3)
            const guestsPerSide = Math.ceil(total / 2);
            const spacing = size[0] / (guestsPerSide + 1);
            
            if (index < guestsPerSide) {
                // Top edge
                x = center[0] - 40; // Above the table
                y = center[1] - size[0]/2 + spacing * (index + 1);
            } else {
                // Bottom edge
                const bottomIndex = index - guestsPerSide;
                x = center[0] + 40; // Below the table
                y = center[1] - size[0]/2 + spacing * (bottomIndex + 1);
            }
        }
        
        return [x, y];
    }

    createGuestAvatar(guest, coords, isCurrent, tableNumber, seatNumber) {
        const isMobile = window.innerWidth <= 768;
        const avatarSize = isMobile ? (isCurrent ? 24 : 20) : (isCurrent ? 28 : 24);
        
        const avatarMarker = L.marker(coords, {
            icon: L.divIcon({
                className: `guest-avatar${isCurrent ? ' current-guest' : ''}`,
                html: `<div class="guest-avatar${isCurrent ? ' current-guest' : ''}" 
                           title="${guest.full_name}"
                           data-guest-name="${guest.full_name}"
                           data-table="${tableNumber}"
                           data-seat="${seatNumber}"
                           style="width: ${avatarSize}px; height: ${avatarSize}px;">
                    ${guest.user.first_name.charAt(0).toUpperCase()}
                </div>`,
                iconSize: [avatarSize, avatarSize],
                iconAnchor: [avatarSize/2, avatarSize/2]
            }),
            zIndexOffset: 1000 // Ensure avatars appear above tables
        }).addTo(this.map);

        // Enhanced click/touch event handling for mobile
        if (isMobile) {
            let touchStartTime;
            let touchMoved = false;
            
            avatarMarker.on('touchstart', (e) => {
                touchStartTime = Date.now();
                touchMoved = false;
                e.originalEvent.preventDefault();
            });
            
            avatarMarker.on('touchmove', () => {
                touchMoved = true;
            });
            
            avatarMarker.on('touchend', (e) => {
                const touchDuration = Date.now() - touchStartTime;
                
                // Only trigger if it was a quick tap (not a drag) and didn't move much
                if (touchDuration < 300 && !touchMoved) {
                    e.originalEvent.stopPropagation();
                    e.originalEvent.preventDefault();
                    this.showGuestModal(guest, tableNumber, seatNumber);
                }
            });
        } else {
            // Desktop click event
            avatarMarker.on('click', (e) => {
                e.originalEvent.stopPropagation();
                this.showGuestModal(guest, tableNumber, seatNumber);
            });
        }

        // Store guest marker
        if (!this.guestMarkers[tableNumber]) {
            this.guestMarkers[tableNumber] = [];
        }
        this.guestMarkers[tableNumber].push(avatarMarker);

        // Add hover tooltip (only for desktop)
        if (!isMobile) {
            avatarMarker.bindTooltip(`<strong>${guest.full_name}</strong><br>Stół ${tableNumber}, Miejsce ${seatNumber}`, {
                direction: 'top',
                offset: [0, -10],
                className: 'guest-tooltip'
            });
        }
    }

    handleTableClick(table) {
        this.clearHighlights();
        this.highlightTable(table.number);
        this.highlightTableCard(table.number);
        
        // Show table popup
        if (this.tableMarkers[table.number]?.shape) {
            this.tableMarkers[table.number].shape.openPopup();
        }
        
        // Animate guest avatars
        this.animateGuestAvatars(table.number);
        
        this.showNotification(`Wybrano stół ${table.number}`, 'success');
    }

    highlightTable(tableNumber) {
        const tableMarker = this.tableMarkers[tableNumber];
        if (!tableMarker) return;

        this.clearHighlights();
        this.currentHighlighted = tableNumber;

        // Update table marker style
        tableMarker.shape.setStyle({
            color: '#2c1810',
            fillColor: '#5d4e37',
            weight: 4
        });

        if (tableMarker.shape instanceof L.Rectangle || tableMarker.shape instanceof L.Circle) {
            tableMarker.shape.getElement()?.classList.add('highlighted');
        }

        // Update label style if it exists
        if (tableMarker.label) {
            const labelElement = tableMarker.label.getElement();
            if (labelElement) {
                const div = labelElement.querySelector('div');
                if (div) {
                    div.style.background = '#5d4e37';
                    div.style.color = '#f5f0e8';
                    div.style.borderColor = '#2c1810';
                }
            }
        }

        // Center map on the table
        const table = tableMarker.table;
        this.map.panTo(this.getTableCenter(table.number));
    }

    getTableCenter(tableNumber) {
        const tablePositions = {
            1: [200, 170], 2: [520, 250], 3: [80, 650], 4: [180, 320], 5: [330, 430],
            6: [360, 320], 7: [510, 430], 8: [540, 320], 9: [690, 430], 10: [720, 320]
        };
        return tablePositions[tableNumber] || [300, 450];
    }

    clearHighlights() {
        Object.values(this.tableMarkers).forEach(({ shape, label }) => {
            shape.setStyle({
                color: '#b8a082',
                fillColor: '#d4c4a8',
                weight: 3
            });

            if (shape.getElement()) {
                shape.getElement().classList.remove('highlighted');
            }

            // Reset label style
            if (label) {
                const labelElement = label.getElement();
                if (labelElement) {
                    const div = labelElement.querySelector('div');
                    if (div) {
                        div.style.background = '#d4c4a8';
                        div.style.color = '#5d4e37';
                        div.style.borderColor = '#b8a082';
                    }
                }
            }
        });

        this.currentHighlighted = null;
        this.clearCardHighlights();
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

    animateGuestAvatars(tableNumber) {
        const guests = this.guestMarkers[tableNumber];
        if (!guests) return;

        guests.forEach((guestMarker, index) => {
            setTimeout(() => {
                const element = guestMarker.getElement();
                if (element) {
                    element.style.animation = 'bounce 0.6s ease';
                    setTimeout(() => {
                        element.style.animation = '';
                    }, 600);
                }
            }, index * 100);
        });
    }

    setupSearch() {
        const searchInput = document.querySelector('#table-search-form input');
        if (!searchInput) return;

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            clearTimeout(this.searchTimeout);
            this.clearHighlights();

            if (query.length < 2) return;

            this.searchTimeout = setTimeout(() => {
                this.performSearch(query);
            }, 300);
        });
    }

    performSearch(query) {
        const searchUrl = window.weddingData?.searchUrl;
        if (!searchUrl) return;

        fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.found && data.table_number && data.table_number !== 'Nie przypisano') {
                    this.highlightTable(parseInt(data.table_number));
                    this.showNotification(`Znaleziono: ${data.guest_name} - Stół ${data.table_number}`, 'success');
                }
            })
            .catch(error => {
                console.error('Search error:', error);
                this.showNotification('Wystąpił błąd podczas wyszukiwania', 'error');
            });
    }

    showGuestModal(guest, tableNumber, seatNumber) {
        const modal = document.getElementById('guest-info-modal');
        if (!modal) return;

        // Update modal content
        document.getElementById('guest-name').textContent = guest.full_name || 'Nieznany gość';
        document.getElementById('guest-table').textContent = tableNumber || '-';
        document.getElementById('guest-type').textContent = guest.guest_type || 'Gość';
        document.getElementById('guest-seat').textContent = seatNumber || 'Nie określono';

        // Show modal
        modal.classList.add('show');

        // Auto-hide after 5 seconds
        clearTimeout(this.guestModalTimeout);
        this.guestModalTimeout = setTimeout(() => {
            this.hideGuestModal();
        }, 5000);
    }

    hideGuestModal() {
        const modal = document.getElementById('guest-info-modal');
        if (modal) {
            modal.classList.remove('show');
        }
        clearTimeout(this.guestModalTimeout);
    }

    setupEventListeners() {
        const isMobile = window.innerWidth <= 768;
        
        // Enhanced modal close handling for mobile
        if (isMobile) {
            // Close modal with swipe down gesture
            let startY, currentY;
            const modal = document.getElementById('guest-info-modal');
            
            if (modal) {
                modal.addEventListener('touchstart', (e) => {
                    startY = e.touches[0].clientY;
                    currentY = startY;
                });
                
                modal.addEventListener('touchmove', (e) => {
                    currentY = e.touches[0].clientY;
                    const diff = currentY - startY;
                    
                    if (diff > 0) {
                        modal.style.transform = `translateY(${diff}px)`;
                        modal.style.opacity = Math.max(0.3, 1 - (diff / 200));
                    }
                });
                
                modal.addEventListener('touchend', () => {
                    const diff = currentY - startY;
                    
                    if (diff > 100) {
                        this.hideGuestModal();
                    } else {
                        // Snap back
                        modal.style.transform = 'translateY(0)';
                        modal.style.opacity = '1';
                    }
                });
            }
        }
        
        // Close modal when clicking outside or pressing Escape
        document.addEventListener('click', (e) => {
            const modal = document.getElementById('guest-info-modal');
            if (modal && modal.classList.contains('show') && 
                !modal.contains(e.target) && 
                !e.target.closest('.guest-avatar') &&
                !e.target.closest('.leaflet-popup')) {
                this.hideGuestModal();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideGuestModal();
            }
        });

        // Handle window resize for mobile optimization with debouncing
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                if (this.map) {
                    this.map.invalidateSize();
                    
                    // Re-optimize for mobile if orientation changed
                    const nowMobile = window.innerWidth <= 768;
                    if (nowMobile !== isMobile) {
                        this.optimizeForMobile(nowMobile);
                    }
                }
            }, 250);
        });

        // Handle orientation change on mobile
        if (isMobile && 'orientation' in screen) {
            screen.orientation.addEventListener('change', () => {
                setTimeout(() => {
                    if (this.map) {
                        this.map.invalidateSize();
                    }
                }, 300);
            });
        }

        // Prevent context menu on long press (mobile)
        if (isMobile) {
            document.addEventListener('contextmenu', (e) => {
                e.preventDefault();
            });
        }

        // Performance optimization: disable hover effects on touch devices
        if (isMobile) {
            const style = document.createElement('style');
            style.textContent = `
                .guest-avatar:hover,
                .table-marker:hover {
                    transform: none !important;
                }
            `;
            document.head.appendChild(style);
        }
    }

    optimizeForMobile(isMobile) {
        // Adjust map settings based on device type
        if (this.map) {
            this.map.options.scrollWheelZoom = !isMobile;
            this.map.options.touchZoom = isMobile;
            
            if (isMobile) {
                this.map.setMinZoom(-2);
                this.map.setMaxZoom(1);
            } else {
                this.map.setMinZoom(-1);
                this.map.setMaxZoom(2);
            }
        }

        // Update avatar sizes
        Object.values(this.guestMarkers).forEach(markers => {
            markers.forEach(marker => {
                const element = marker.getElement();
                if (element) {
                    const avatar = element.querySelector('.guest-avatar');
                    if (avatar) {
                        const isCurrent = avatar.classList.contains('current-guest');
                        const size = isMobile ? (isCurrent ? 24 : 20) : (isCurrent ? 28 : 24);
                        avatar.style.width = `${size}px`;
                        avatar.style.height = `${size}px`;
                    }
                }
            });
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 250px; animation: slideInRight 0.3s ease;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="close" onclick="this.parentElement.remove()">
                <span>&times;</span>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 3000);
    }
}

// Global function for modal close button
window.hideGuestModal = function() {
    if (window.weddingTableMap) {
        window.weddingTableMap.hideGuestModal();
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
    `;
    document.head.appendChild(style);
    
    // Initialize the wedding table map
    if (document.getElementById('wedding-map')) {
        window.weddingTableMap = new WeddingTableMap();
    }
});