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
    
    const radius = 60; // Distance from table center
    const angleStep = (360 / totalAvatars);
    
    avatars.forEach((avatar, index) => {
        const angle = angleStep * index - 90; // Start from top
        const radian = (angle * Math.PI) / 180;
        
        const x = Math.cos(radian) * radius;
        const y = Math.sin(radian) * radius;
        
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

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification-toast');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification-toast notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)}"></i>
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getColorForType(type)};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 10px;
        max-width: 300px;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
    
    // Manual close
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    });
}

function getIconForType(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        info: 'info-circle',
        warning: 'exclamation-triangle'
    };
    return icons[type] || 'info-circle';
}

function getColorForType(type) {
    const colors = {
        success: 'linear-gradient(135deg, #28a745, #20c997)',
        error: 'linear-gradient(135deg, #dc3545, #e74c3c)',
        info: 'linear-gradient(135deg, #17a2b8, #007bff)',
        warning: 'linear-gradient(135deg, #ffc107, #fd7e14)'
    };
    return colors[type] || colors.info;
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