// DEBUG VERSION - Wedding Table Map with Leaflet.js
console.log('🚀 Loading DEBUG version of wedding map...');

class WeddingTableMapDebug {
    constructor() {
        console.log('🏗️ Constructing WeddingTableMapDebug...');
        this.map = null;
        this.tableMarkers = {};
        this.guestMarkers = {};
        this.currentHighlighted = null;
        this.searchTimeout = null;
        this.currentGuestInfo = window.weddingData?.currentGuestInfo || null;
        
        console.log('📊 Wedding data:', window.weddingData);
        console.log('👤 Current guest:', this.currentGuestInfo);
        
        this.init();
    }

    init() {
        console.log('🔧 Initializing map...');
        try {
            this.createMap();
            console.log('✅ Map created successfully');
            
            this.addTables();
            console.log('✅ Tables added');
            
            this.setupSearch();
            console.log('✅ Search setup complete');
            
            this.setupEventListeners();
            console.log('✅ Event listeners setup');
            
        } catch (error) {
            console.error('❌ Error in init:', error);
        }
    }

    createMap() {
        console.log('🗺️ Creating Leaflet map...');
        
        const isMobile = window.innerWidth <= 768;
        console.log('📱 Is mobile:', isMobile);
        
        this.map = L.map('wedding-map', {
            crs: L.CRS.Simple,
            minZoom: isMobile ? -2 : -1,
            maxZoom: isMobile ? 1 : 2,
            zoomControl: false,
            attributionControl: false,
            scrollWheelZoom: !isMobile,
            doubleClickZoom: true,
            touchZoom: isMobile,
            dragging: true,
            tap: isMobile,
            tapTolerance: 15
        });

        const bounds = [[0, 0], [600, 900]];
        this.map.fitBounds(bounds);
        this.map.setMaxBounds(bounds.map(bound => [bound[0] - 50, bound[1] - 50]));

        // Add zoom controls
        const zoomControl = L.control.zoom({
            position: 'topright'
        });
        zoomControl.addTo(this.map);

        // Add test background
        this.addBackgroundPattern();
        
        console.log('✅ Map created with bounds:', bounds);
    }

    addBackgroundPattern() {
        console.log('🎨 Adding background pattern...');
        
        // Add venue background
        const venueBackground = L.rectangle([[50, 100], [550, 800]], {
            color: 'transparent',
            fillColor: '#f8f5f0',
            fillOpacity: 0.3,
            weight: 0
        }).addTo(this.map);

        // Add dance floor
        const danceFloor = L.circle([300, 450], {
            radius: 80,
            color: '#d4c4a8',
            fillColor: '#ede8dd',
            fillOpacity: 0.5,
            weight: 2,
            dashArray: '5, 5'
        }).addTo(this.map);

        danceFloor.bindTooltip('🕺 Parkiet Taneczny');
        
        console.log('✅ Background pattern added');
    }

    addTables() {
        console.log('🪑 Adding tables...');
        
        const tables = window.weddingData?.tables || [];
        console.log('📋 Tables data:', tables);
        console.log('🔢 Number of tables:', tables.length);
        
        if (tables.length === 0) {
            console.error('❌ No tables found in window.weddingData.tables!');
            console.log('🔍 Available data keys:', Object.keys(window.weddingData || {}));
            
            // Add test tables if no data
            console.log('➕ Adding test tables...');
            this.addTestTables();
            return;
        }
        
        // Table positions
        const tablePositions = {
            1: { coords: [200, 170], size: [65, 200], type: 'rectangular' },
            2: { coords: [520, 250], size: [500, 65], type: 'rectangular' },
            3: { coords: [80, 650], size: [600, 65], type: 'rectangular' },
            4: { coords: [180, 320], size: [85, 85], type: 'circular' },
            5: { coords: [330, 430], size: [85, 85], type: 'circular' },
            6: { coords: [360, 320], size: [85, 85], type: 'circular' },
            7: { coords: [510, 430], size: [85, 85], type: 'circular' },
            8: { coords: [540, 320], size: [85, 85], type: 'circular' },
            9: { coords: [690, 430], size: [85, 85], type: 'circular' },
            10: { coords: [720, 320], size: [85, 85], type: 'circular' }
        };

        tables.forEach(table => {
            console.log(`🪑 Processing table ${table.number}:`, table);
            const position = tablePositions[table.number];
            if (!position) {
                console.warn(`❓ No position found for table ${table.number}`);
                return;
            }

            try {
                this.createTableMarker(table, position);
                console.log(`✅ Table ${table.number} created successfully`);
            } catch (error) {
                console.error(`❌ Error creating table ${table.number}:`, error);
            }
        });
        
        console.log('✅ All tables processed');
    }

    addTestTables() {
        console.log('🧪 Adding test tables...');
        
        const testTables = [
            { number: 1, name: 'Test Table 1', capacity: 8, guests_count: 3 },
            { number: 4, name: 'Test Table 4', capacity: 8, guests_count: 5 },
            { number: 6, name: 'Test Table 6', capacity: 8, guests_count: 2 }
        ];

        const tablePositions = {
            1: { coords: [200, 170], size: [65, 200], type: 'rectangular' },
            4: { coords: [180, 320], size: [85, 85], type: 'circular' },
            6: { coords: [360, 320], size: [85, 85], type: 'circular' }
        };

        testTables.forEach(table => {
            const position = tablePositions[table.number];
            if (position) {
                try {
                    this.createSimpleTableMarker(table, position);
                    console.log(`✅ Test table ${table.number} added`);
                } catch (error) {
                    console.error(`❌ Error creating test table ${table.number}:`, error);
                }
            }
        });
    }

    createSimpleTableMarker(table, position) {
        const { coords, size, type } = position;
        
        let marker;
        
        if (type === 'rectangular') {
            const bounds = [
                [coords[0] - size[1]/2, coords[1] - size[0]/2],
                [coords[0] + size[1]/2, coords[1] + size[0]/2]
            ];
            
            marker = L.rectangle(bounds, {
                color: '#b8a082',
                fillColor: '#d4c4a8',
                fillOpacity: 0.8,
                weight: 3
            }).addTo(this.map);
        } else {
            marker = L.circle(coords, {
                radius: size[0]/2,
                color: '#b8a082',
                fillColor: '#d4c4a8',
                fillOpacity: 0.8,
                weight: 3
            }).addTo(this.map);
        }
        
        // Add label
        const labelMarker = L.marker(coords, {
            icon: L.divIcon({
                className: 'table-number-label',
                html: `<div style="background: #d4c4a8; color: #5d4e37; border: 3px solid #b8a082; border-radius: ${type === 'rectangular' ? '8px' : '50%'}; padding: 8px 12px; font-weight: bold; font-size: 1.2rem; box-shadow: 0 4px 15px rgba(93, 78, 55, 0.3); text-align: center; min-width: 40px;">${table.number}</div>`,
                iconSize: [50, 30],
                iconAnchor: [25, 15]
            })
        }).addTo(this.map);
        
        // Add popup
        const popupContent = `
            <div style="font-family: Georgia, serif;">
                <h4>Stół ${table.number}</h4>
                <p><strong>${table.name}</strong></p>
                <p>Gości: ${table.guests_count}/${table.capacity}</p>
                <p><em>Test table - brak prawdziwych danych</em></p>
            </div>
        `;
        marker.bindPopup(popupContent);
        
        this.tableMarkers[table.number] = { shape: marker, label: labelMarker, table: table };
    }

    createTableMarker(table, position) {
        console.log(`🏗️ Creating marker for table ${table.number}`, position);
        // ... rest of the original method
        
        const { coords, size, type } = position;
        const isHighlighted = this.currentGuestInfo && this.currentGuestInfo.table_number === table.number;
        
        let marker;
        
        if (type === 'rectangular') {
            const bounds = [
                [coords[0] - size[1]/2, coords[1] - size[0]/2],
                [coords[0] + size[1]/2, coords[1] + size[0]/2]
            ];
            
            marker = L.rectangle(bounds, {
                color: isHighlighted ? '#2c1810' : '#b8a082',
                fillColor: isHighlighted ? '#5d4e37' : '#d4c4a8',
                fillOpacity: 0.8,
                weight: 3,
                className: `table-marker rectangular${isHighlighted ? ' highlighted' : ''}`
            }).addTo(this.map);
            
        } else {
            marker = L.circle(coords, {
                radius: size[0]/2,
                color: isHighlighted ? '#2c1810' : '#b8a082',
                fillColor: isHighlighted ? '#5d4e37' : '#d4c4a8',
                fillOpacity: 0.8,
                weight: 3,
                className: `table-marker${isHighlighted ? ' highlighted' : ''}`
            }).addTo(this.map);
        }

        // Add table number label
        const labelMarker = L.marker(coords, {
            icon: L.divIcon({
                className: 'table-number-label',
                html: `<div style="background: ${isHighlighted ? '#5d4e37' : '#d4c4a8'}; color: ${isHighlighted ? '#f5f0e8' : '#5d4e37'}; border: 3px solid ${isHighlighted ? '#2c1810' : '#b8a082'}; border-radius: ${type === 'rectangular' ? '8px' : '50%'}; padding: 8px 12px; font-weight: bold; font-size: 1.2rem; box-shadow: 0 4px 15px rgba(93, 78, 55, 0.3); text-align: center; min-width: 40px;">${table.number}</div>`,
                iconSize: [50, 30],
                iconAnchor: [25, 15]
            })
        }).addTo(this.map);
        
        this.tableMarkers[table.number] = { shape: marker, label: labelMarker, table: table };

        // Add popup
        const popupContent = this.createTablePopup(table);
        marker.bindPopup(popupContent, {
            maxWidth: 250,
            className: 'table-popup-container'
        });

        // Add guests if available
        if (table.guest_list && table.guest_list.length > 0) {
            console.log(`👥 Adding ${table.guest_list.length} guests to table ${table.number}`);
            this.addGuestAvatars(table, coords, type, size);
        } else {
            console.log(`👤 No guests found for table ${table.number}`);
        }

        console.log(`✅ Table ${table.number} marker created successfully`);
    }

    createTablePopup(table) {
        const currentGuest = this.currentGuestInfo;
        let guestsHtml = '';
        
        if (table.guest_list && table.guest_list.length > 0) {
            guestsHtml = table.guest_list.map(guest => {
                const isCurrent = currentGuest && currentGuest.id === guest.id;
                return `<span style="display: inline-block; background: ${isCurrent ? '#8b6f47' : '#d4c4a8'}; color: ${isCurrent ? '#f5f0e8' : '#5d4e37'}; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; margin: 2px;">${guest.full_name}</span>`;
            }).join('');
        }

        return `
            <div style="font-family: Georgia, serif;">
                <h4>Stół ${table.number}</h4>
                <p><strong>${table.name}</strong></p>
                <p>${table.description}</p>
                <p>Zajętość: ${table.guests_count}/${table.capacity} miejsc</p>
                ${guestsHtml ? `<div style="margin-top: 10px;">${guestsHtml}</div>` : ''}
            </div>
        `;
    }

    addGuestAvatars(table, coords, type, size) {
        console.log(`👥 Adding guest avatars for table ${table.number}:`, table.guest_list);
        
        if (!table.guest_list || table.guest_list.length === 0) return;

        const guests = table.guest_list;
        const totalGuests = guests.length;
        
        guests.forEach((guest, index) => {
            try {
                const isCurrent = this.currentGuestInfo && this.currentGuestInfo.id === guest.id;
                let avatarCoords;

                if (type === 'rectangular') {
                    avatarCoords = this.calculateRectangularAvatarPosition(coords, size, index, totalGuests, table.number);
                } else {
                    avatarCoords = this.calculateCircularAvatarPosition(coords, index, totalGuests);
                }

                if (avatarCoords) {
                    this.createGuestAvatar(guest, avatarCoords, isCurrent, table.number, index + 1);
                    console.log(`✅ Avatar created for ${guest.full_name}`);
                }
            } catch (error) {
                console.error(`❌ Error creating avatar for ${guest.full_name}:`, error);
            }
        });
    }

    calculateCircularAvatarPosition(center, index, total) {
        const radius = 55;
        const angle = (360 / total) * index - 90;
        const radian = (angle * Math.PI) / 180;
        
        return [
            center[0] + Math.sin(radian) * radius,
            center[1] + Math.cos(radian) * radius
        ];
    }

    calculateRectangularAvatarPosition(center, size, index, total, tableNumber) {
        let x, y;
        
        if (tableNumber === 1) {
            const spacing = size[1] / (total + 1);
            x = center[0] - 60;
            y = center[0] - size[1]/2 + spacing * (index + 1);
        } else {
            const guestsPerSide = Math.ceil(total / 2);
            const spacing = size[0] / (guestsPerSide + 1);
            
            if (index < guestsPerSide) {
                x = center[0] - 40;
                y = center[1] - size[0]/2 + spacing * (index + 1);
            } else {
                const bottomIndex = index - guestsPerSide;
                x = center[0] + 40;
                y = center[1] - size[0]/2 + spacing * (bottomIndex + 1);
            }
        }
        
        return [x, y];
    }

    createGuestAvatar(guest, coords, isCurrent, tableNumber, seatNumber) {
        console.log(`👤 Creating avatar for ${guest.full_name} at table ${tableNumber}`);
        
        const isMobile = window.innerWidth <= 768;
        const avatarSize = isMobile ? (isCurrent ? 24 : 20) : (isCurrent ? 28 : 24);
        
        const avatarMarker = L.marker(coords, {
            icon: L.divIcon({
                className: `guest-avatar${isCurrent ? ' current-guest' : ''}`,
                html: `<div style="width: ${avatarSize}px; height: ${avatarSize}px; border-radius: 50%; background: linear-gradient(145deg, ${isCurrent ? '#d4a574, #b8935f' : '#8b6f47, #5d4e37'}); border: 2px solid #f5f0e8; display: flex; align-items: center; justify-content: center; font-size: ${avatarSize * 0.4}px; color: #f5f0e8; font-weight: bold; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3); cursor: pointer;">
                    ${guest.user ? guest.user.first_name.charAt(0).toUpperCase() : guest.full_name.charAt(0).toUpperCase()}
                </div>`,
                iconSize: [avatarSize, avatarSize],
                iconAnchor: [avatarSize/2, avatarSize/2]
            }),
            zIndexOffset: 1000
        }).addTo(this.map);

        // Store guest marker
        if (!this.guestMarkers[tableNumber]) {
            this.guestMarkers[tableNumber] = [];
        }
        this.guestMarkers[tableNumber].push(avatarMarker);

        // Add tooltip
        if (!isMobile) {
            avatarMarker.bindTooltip(`<strong>${guest.full_name}</strong><br>Stół ${tableNumber}, Miejsce ${seatNumber}`, {
                direction: 'top',
                offset: [0, -10],
                className: 'guest-tooltip'
            });
        }
        
        console.log(`✅ Avatar created for ${guest.full_name}`);
    }

    setupSearch() {
        console.log('🔍 Setting up search...');
        // Simplified for debug
    }

    setupEventListeners() {
        console.log('🎧 Setting up event listeners...');
        // Simplified for debug
    }

    showNotification(message, type = 'info') {
        console.log(`📢 Notification (${type}): ${message}`);
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 250px;';
        notification.innerHTML = `${message} <button type="button" class="close" onclick="this.parentElement.remove()"><span>&times;</span></button>`;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌟 DOM loaded, starting wedding map debug...');
    
    if (document.getElementById('wedding-map')) {
        console.log('✅ Map container found');
        window.weddingTableMapDebug = new WeddingTableMapDebug();
    } else {
        console.error('❌ Map container not found!');
    }
});