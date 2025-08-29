// Main wedding app JavaScript

$(document).ready(function() {
    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();
    
    // Photo lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Smooth scroll to top after navigation
    $('.nav-item').on('click', function() {
        setTimeout(function() {
            $('html, body').animate({scrollTop: 0}, 'smooth');
        }, 100);
    });
    
    // Auto-hide alerts
    $('.alert').each(function() {
        const alert = $(this);
        setTimeout(function() {
            alert.fadeOut();
        }, 5000);
    });
    
    // Photo upload preview
    $('#id_image').change(function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = $('<div class="preview-container"><img src="' + e.target.result + '" class="img-thumbnail" style="max-width: 200px;"><p>Podgląd zdjęcia</p></div>');
                $('#id_image').after(preview);
                $('.preview-container').fadeIn();
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Enhanced table search with debouncing
    let searchTimeout;
    $('#table-search-input').on('input', function() {
        const query = $(this).val();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            $('#search-results').hide();
            return;
        }
        
        searchTimeout = setTimeout(function() {
            $.get('/api/guest-search/', {q: query})
                .done(function(data) {
                    if (data.results.length > 0) {
                        let html = '<div class="search-results-dropdown">';
                        data.results.forEach(function(guest) {
                            html += `<div class="search-result-item" data-guest-id="${guest.id}">
                                <strong>${guest.name}</strong><br>
                                <small>Stół ${guest.table_number || 'nie przypisano'}</small>
                            </div>`;
                        });
                        html += '</div>';
                        
                        $('#search-results').html(html).show();
                    } else {
                        $('#search-results').html('<div class="no-results">Nie znaleziono gościa</div>').show();
                    }
                })
                .fail(function() {
                    $('#search-results').html('<div class="error">Błąd podczas wyszukiwania</div>').show();
                });
        }, 300);
    });
    
    // Click outside to hide search results
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#table-search-form').length) {
            $('#search-results').hide();
        }
    });
    
    // Infinite scroll for gallery
    if ($('.photo-grid').length) {
        let loading = false;
        let page = 2;
        const category = new URLSearchParams(window.location.search).get('category') || '';
        
        $(window).scroll(function() {
            if (loading) return;
            
            if ($(window).scrollTop() + $(window).height() > $(document).height() - 1000) {
                loading = true;
                $('.loading-indicator').show();
                
                $.get('/api/photos/', {page: page, category: category})
                    .done(function(data) {
                        if (data.photos.length > 0) {
                            data.photos.forEach(function(photo) {
                                const photoHtml = `
                                    <div class="photo-item" data-toggle="modal" data-target="#photoModal${photo.id}">
                                        <img src="${photo.image_url || photo.full_image_url || '/static/wedding/images/no-photo.jpg'}" 
                                             alt="${photo.title}" 
                                             loading="lazy"
                                             onerror="this.onerror=null; this.src='${photo.full_image_url || '/static/wedding/images/no-photo.jpg'}';">
                                        <div class="photo-overlay">
                                            <h6>${photo.title}</h6>
                                            <small>${photo.uploaded_by}</small>
                                        </div>
                                    </div>
                                `;
                                $('.photo-grid').append(photoHtml);
                            });
                            page++;
                        }
                        
                        if (!data.has_next) {
                            $('.loading-indicator').html('Wszystkie zdjęcia zostały załadowane').show();
                        }
                    })
                    .always(function() {
                        loading = false;
                        if ($('.photo-grid .photo-item').length > 0) {
                            $('.loading-indicator').hide();
                        }
                    });
            }
        });
    }
    
    // Progressive Web App features
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    }
    
    // Install PWA prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Show install button
        const installBtn = $('<button class="btn btn-custom-primary install-btn">Dodaj do ekranu głównego</button>');
        $('.nav-menu').after(installBtn);
        
        installBtn.on('click', () => {
            installBtn.hide();
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                }
                deferredPrompt = null;
            });
        });
    });
});

// Notification system
class WeddingNotifications {
    static show(message, type = 'info') {
        const alertClass = type === 'error' ? 'alert-danger' : `alert-${type}`;
        const alert = $(`
            <div class="alert ${alertClass} alert-dismissible fade show notification" role="alert">
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        `);
        
        $('body').prepend(alert);
        
        setTimeout(() => {
            alert.fadeOut(() => alert.remove());
        }, 5000);
    }
    
    static success(message) {
        this.show(message, 'success');
    }
    
    static error(message) {
        this.show(message, 'error');
    }
    
    static info(message) {
        this.show(message, 'info');
    }
}

// Export for global use
window.WeddingNotifications = WeddingNotifications;