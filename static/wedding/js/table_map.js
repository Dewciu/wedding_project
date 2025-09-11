// Enhanced Table Map JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeTableMap();
    initializeSearch();
    initializeTooltips();
    initializeAnimations();
});

function initializeTableMap() {
    const tableCircles = document.querySelectorAll('.table-circle');
    
    tableCircles.forEach((circle, index) => {
        // Add entrance animation with staggered delay
        circle.style.animationDelay = `${index * 0.1}s`;
        circle.classList.add('fade-in');
        
        // Position guest avatars around the table
        positionGuestAvatars(circle);
        
        // Add click handler
        circle.addEventListener('click', function() {
            handleTableClick(this);
        });
        
        // Add hover effects
        circle.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            showTableInfo(this);
        });
        
        circle.addEventListener('mouseleave', function() {
            if (!this.classList.contains('highlighted')) {
                this.style.transform = 'scale(1)';
            }
            hideTableInfo(this);
        });
    });
}

function positionGuestAvatars(tableCircle) {
    const avatars = tableCircle.querySelectorAll('.guest-avatar');
    const totalAvatars = avatars.length;
    
    if (totalAvatars === 0) return;
    
    // Get table shape info
    const tableShape = tableCircle.dataset.shape || 'circular';
    const tableWidth = parseFloat(tableCircle.dataset.width) || 85;
    const tableHeight = parseFloat(tableCircle.dataset.height) || 85;
    
    avatars.forEach((avatar, index) => {
        let x, y;
        
        if (tableShape === 'rectangular' || tableShape === 'square') {
            // Rectangular table positioning logic
            const margin = 35; // Reduced from 45 to 35 for closer positioning
            
            if (tableWidth > tableHeight) {
                // Horizontal table - guests at top and bottom
                const spacing = tableWidth / (totalAvatars + 1);
                const offsetFromCenter = -tableWidth/2 + spacing * (index + 1);
                
                if (index % 2 === 0) {
                    // Even indices - top edge
                    x = offsetFromCenter;
                    y = -margin;
                } else {
                    // Odd indices - bottom edge
                    x = offsetFromCenter;
                    y = margin;
                }
            } else {
                // Vertical table - guests only at left edge
                const spacing = tableHeight / (totalAvatars + 1);
                const offsetFromCenter = -tableHeight/2 + spacing * (index + 1);
                
                // All guests on left edge
                x = -margin;
                y = offsetFromCenter;
            }
        } else {
            // Circular table positioning (original logic)
            const radius = 55; // Reduced from 75 to 55 for better positioning closer to table
            const angleStep = (360 / totalAvatars);
            const angle = angleStep * index - 90; // Start from top
            const radian = (angle * Math.PI) / 180;
            
            x = Math.cos(radian) * radius;
            y = Math.sin(radian) * radius;
        }
        
        // Apply position with smooth animation
        avatar.style.transform = `translate(${x}px, ${y}px) scale(0)`;
        avatar.style.opacity = '0';
        
        // Animate in with delay
        setTimeout(() => {
            avatar.style.transition = 'all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            avatar.style.transform = `translate(${x}px, ${y}px) scale(1)`;
            avatar.style.opacity = '1';
        }, 200 + (index * 50));
        
        // Add hover effect for avatars
        avatar.addEventListener('mouseenter', function() {
            this.style.transform = `translate(${x}px, ${y}px) scale(1.3)`;
            showGuestTooltip(this);
        });
        
        avatar.addEventListener('mouseleave', function() {
            this.style.transform = `translate(${x}px, ${y}px) scale(1)`;
            hideGuestTooltip();
        });
        
        // Add drag functionality for chair positioning
        makeDraggable(avatar, tableCircle, index);
    });
}

function handleTableClick(tableCircle) {
    const tableNumber = tableCircle.dataset.table;
    
    // Remove highlighting from other tables
    document.querySelectorAll('.table-circle').forEach(circle => {
        if (circle !== tableCircle) {
            circle.classList.remove('highlighted');
            circle.style.transform = 'scale(1)';
        }
    });
    
    // Toggle highlighting on clicked table
    const isHighlighted = tableCircle.classList.toggle('highlighted');
    
    if (isHighlighted) {
        tableCircle.style.transform = 'scale(1.1)';
        showTableDetails(tableNumber);
        
        // Animate guest avatars
        const avatars = tableCircle.querySelectorAll('.guest-avatar');
        avatars.forEach((avatar, index) => {
            setTimeout(() => {
                avatar.style.animation = 'bounce 0.6s ease';
            }, index * 100);
        });
    } else {
        tableCircle.style.transform = 'scale(1)';
        hideTableDetails();
    }
    
    // Scroll to table details if on mobile
    if (window.innerWidth < 768 && isHighlighted) {
        scrollToTableDetails(tableNumber);
    }
}

function showTableDetails(tableNumber) {
    const tableCard = document.querySelector(`[data-table-card="${tableNumber}"]`);
    if (tableCard) {
        tableCard.style.border = '2px solid #8b6f47';
        tableCard.style.transform = 'scale(1.02)';
        tableCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function hideTableDetails() {
    document.querySelectorAll('[data-table-card]').forEach(card => {
        card.style.border = '';
        card.style.transform = '';
    });
}

function scrollToTableDetails(tableNumber) {
    const detailsSection = document.querySelector('.row.mt-4');
    if (detailsSection) {
        detailsSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
}

function initializeSearch() {
    const searchForm = document.getElementById('table-search-form');
    const searchInput = searchForm?.querySelector('input');
    
    if (!searchInput) return;
    
    let searchTimeout;
    let searchResults = null;
    
    // Enhanced search with real-time feedback
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(searchTimeout);
        
        // Clear previous results
        clearSearchHighlights();
        
        if (query.length < 2) {
            hideSearchResults();
            return;
        }
        
        // Show loading indicator
        showSearchLoading();
        
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    // Handle form submission
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query.length >= 2) {
            performSearch(query);
        }
    });
}

function performSearch(query) {
    // AJAX search
    fetch(`/ajax/table-search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            hideSearchLoading();
            
            if (data.found) {
                highlightGuestTable(data);
                showSearchSuccess(data);
            } else {
                showSearchNoResults();
            }
        })
        .catch(error => {
            console.error('Search error:', error);
            hideSearchLoading();
            showSearchError();
        });
}

function highlightGuestTable(guestData) {
    clearSearchHighlights();
    
    if (!guestData.table_number || guestData.table_number === 'Nie przypisano') {
        return;
    }
    
    const tableCircle = document.querySelector(`[data-table="${guestData.table_number}"]`);
    if (tableCircle) {
        tableCircle.classList.add('highlighted');
        tableCircle.style.transform = 'scale(1.1)';
        
        // Highlight guest avatar
        const guestAvatar = tableCircle.querySelector(`[title*="${guestData.guest_name}"]`);
        if (guestAvatar) {
            guestAvatar.classList.add('current-guest');
        }
        
        // Scroll to table with smooth animation
        setTimeout(() => {
            tableCircle.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }, 100);
    }
}

function clearSearchHighlights() {
    document.querySelectorAll('.table-circle').forEach(circle => {
        circle.classList.remove('highlighted');
        circle.style.transform = 'scale(1)';
    });
    
    document.querySelectorAll('.guest-avatar').forEach(avatar => {
        avatar.classList.remove('current-guest');
    });
}

function showSearchLoading() {
    const searchBtn = document.querySelector('#table-search-form button');
    if (searchBtn) {
        searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Szukam...';
        searchBtn.disabled = true;
    }
}

function hideSearchLoading() {
    const searchBtn = document.querySelector('#table-search-form button');
    if (searchBtn) {
        searchBtn.innerHTML = '<i class="fas fa-search"></i> Szukaj';
        searchBtn.disabled = false;
    }
}

function showSearchSuccess(data) {
    showNotification(`Znaleziono: ${data.guest_name} - Stół ${data.table_number}`, 'success');
}

function showSearchNoResults() {
    showNotification('Nie znaleziono gościa o tym imieniu', 'info');
}

function showSearchError() {
    showNotification('Wystąpił błąd podczas wyszukiwania', 'error');
}

function initializeTooltips() {
    // Dynamic tooltips for guest avatars
    document.querySelectorAll('.guest-avatar').forEach(avatar => {
        avatar.addEventListener('mouseenter', function() {
            const guestName = this.title || this.getAttribute('data-guest-name');
            if (guestName) {
                showGuestTooltip(this, guestName);
            }
        });
        
        avatar.addEventListener('mouseleave', function() {
            hideGuestTooltip();
        });
    });
}

function showGuestTooltip(element, guestName) {
    // Remove existing tooltips
    hideGuestTooltip();
    
    const tooltip = document.createElement('div');
    tooltip.className = 'guest-tooltip';
    tooltip.innerHTML = guestName;
    tooltip.style.cssText = `
        position: absolute;
        background: rgba(93, 78, 55, 0.95);
        color: #f5f0e8;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.8rem;
        white-space: nowrap;
        z-index: 1000;
        pointer-events: none;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        animation: fadeIn 0.2s ease;
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
    
    // Adjust if tooltip goes off screen
    const tooltipRect = tooltip.getBoundingClientRect();
    if (tooltipRect.left < 10) {
        tooltip.style.left = '10px';
    } else if (tooltipRect.right > window.innerWidth - 10) {
        tooltip.style.left = `${window.innerWidth - tooltipRect.width - 10}px`;
    }
    
    if (tooltipRect.top < 10) {
        tooltip.style.top = `${rect.bottom + 8}px`;
    }
}

function hideGuestTooltip() {
    const existingTooltip = document.querySelector('.guest-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
}

function initializeAnimations() {
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.card-custom, .timeline-item, .menu-item').forEach(el => {
        observer.observe(el);
    });
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .animate-in {
        animation: fadeIn 0.6s ease forwards;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 1.2rem;
        cursor: pointer;
        padding: 0;
        margin-left: auto;
    }
    
    .notification-close:hover {
        opacity: 0.7;
    }
    `;
document.head.appendChild(style);

// Drag and Drop functionality for guest positioning
function makeDraggable(avatar, tableCircle, originalIndex) {
    let isDragging = false;
    let dragStartX, dragStartY;
    let originalTransform;
    
    avatar.style.cursor = 'grab';
    
    // Mouse events
    avatar.addEventListener('mousedown', startDrag);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', endDrag);
    
    // Touch events for mobile
    avatar.addEventListener('touchstart', startDragTouch, {passive: false});
    document.addEventListener('touchmove', dragTouch, {passive: false});
    document.addEventListener('touchend', endDragTouch);
    
    function startDrag(e) {
        e.preventDefault();
        isDragging = true;
        avatar.style.cursor = 'grabbing';
        avatar.style.zIndex = '1000';
        
        const rect = avatar.getBoundingClientRect();
        const tableRect = tableCircle.getBoundingClientRect();
        
        dragStartX = e.clientX - tableRect.left - tableRect.width/2;
        dragStartY = e.clientY - tableRect.top - tableRect.height/2;
        originalTransform = avatar.style.transform;
        
        avatar.style.transform = `translate(${dragStartX}px, ${dragStartY}px) scale(1.2)`;
        avatar.classList.add('dragging');
    }
    
    function startDragTouch(e) {
        e.preventDefault();
        const touch = e.touches[0];
        startDrag({
            clientX: touch.clientX,
            clientY: touch.clientY,
            preventDefault: () => {}
        });
    }
    
    function drag(e) {
        if (!isDragging) return;
        e.preventDefault();
        
        const tableRect = tableCircle.getBoundingClientRect();
        const x = e.clientX - tableRect.left - tableRect.width/2;
        const y = e.clientY - tableRect.top - tableRect.height/2;
        
        avatar.style.transform = `translate(${x}px, ${y}px) scale(1.2)`;
    }
    
    function dragTouch(e) {
        if (!isDragging) return;
        e.preventDefault();
        const touch = e.touches[0];
        drag({
            clientX: touch.clientX,
            clientY: touch.clientY,
            preventDefault: () => {}
        });
    }
    
    function endDrag(e) {
        if (!isDragging) return;
        isDragging = false;
        
        avatar.style.cursor = 'grab';
        avatar.style.zIndex = '';
        avatar.classList.remove('dragging');
        
        // Calculate final position and snap to nearest chair position
        const tableRect = tableCircle.getBoundingClientRect();
        const finalX = e.clientX - tableRect.left - tableRect.width/2;
        const finalY = e.clientY - tableRect.top - tableRect.height/2;
        
        snapToChairPosition(avatar, tableCircle, finalX, finalY);
    }
    
    function endDragTouch(e) {
        if (!isDragging) return;
        const touch = e.changedTouches[0];
        endDrag({
            clientX: touch.clientX,
            clientY: touch.clientY
        });
    }
}

function snapToChairPosition(avatar, tableCircle, x, y) {
    const tableShape = tableCircle.dataset.shape || 'circular';
    const tableWidth = parseFloat(tableCircle.dataset.width) || 85;
    const tableHeight = parseFloat(tableCircle.dataset.height) || 85;
    const allAvatars = tableCircle.querySelectorAll('.guest-avatar');
    const totalAvatars = allAvatars.length;
    
    let bestPosition = 0;
    let minDistance = Infinity;
    
    // Calculate possible chair positions
    const chairPositions = calculateChairPositions(tableShape, tableWidth, tableHeight, totalAvatars);
    
    // Find closest chair position
    chairPositions.forEach((pos, index) => {
        const distance = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2);
        if (distance < minDistance) {
            minDistance = distance;
            bestPosition = index;
        }
    });
    
    // Check if position is available (not occupied by another guest)
    const occupiedPositions = Array.from(allAvatars)
        .filter(a => a !== avatar)
        .map(a => parseInt(a.dataset.chairPosition) || 0)
        .filter(pos => pos > 0);
    
    if (occupiedPositions.includes(bestPosition + 1)) {
        // Find nearest available position
        for (let i = 0; i < chairPositions.length; i++) {
            if (!occupiedPositions.includes(i + 1)) {
                bestPosition = i;
                break;
            }
        }
    }
    
    // Snap to position
    const finalPos = chairPositions[bestPosition];
    avatar.style.transform = `translate(${finalPos.x}px, ${finalPos.y}px) scale(1)`;
    avatar.dataset.chairPosition = bestPosition + 1;
    
    // Update in database
    updateChairPositionInDatabase(avatar.dataset.guestId, bestPosition + 1);
}

function calculateChairPositions(tableShape, tableWidth, tableHeight, totalChairs) {
    const positions = [];
    
    if (tableShape === 'rectangular' || tableShape === 'square') {
        const margin = 35;
        
        if (tableWidth > tableHeight) {
            // Horizontal table
            const spacing = tableWidth / (totalChairs + 1);
            for (let i = 0; i < totalChairs; i++) {
                const offsetFromCenter = -tableWidth/2 + spacing * (i + 1);
                positions.push({
                    x: offsetFromCenter,
                    y: i % 2 === 0 ? -margin : margin
                });
            }
        } else {
            // Vertical table
            const spacing = tableHeight / (totalChairs + 1);
            for (let i = 0; i < totalChairs; i++) {
                const offsetFromCenter = -tableHeight/2 + spacing * (i + 1);
                positions.push({
                    x: -margin,
                    y: offsetFromCenter
                });
            }
        }
    } else {
        // Circular table
        const radius = 55;
        const angleStep = 360 / totalChairs;
        for (let i = 0; i < totalChairs; i++) {
            const angle = angleStep * i - 90;
            const radian = (angle * Math.PI) / 180;
            positions.push({
                x: Math.cos(radian) * radius,
                y: Math.sin(radian) * radius
            });
        }
    }
    
    return positions;
}

function updateChairPositionInDatabase(guestId, chairPosition) {
    if (!guestId) return;
    
    fetch('/ajax/update-chair-position/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            guest_id: guestId,
            chair_position: chairPosition
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Pozycja krzesła zaktualizowana:', data.message);
            showNotification('✅ Pozycja gościa została zapisana', 'success');
        } else {
            console.error('Błąd aktualizacji:', data.message);
            showNotification('❌ Błąd zapisywania pozycji', 'error');
        }
    })
    .catch(error => {
        console.error('Błąd sieci:', error);
        showNotification('❌ Błąd połączenia', 'error');
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
    
    // Manual close
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });
}