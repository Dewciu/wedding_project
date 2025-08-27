// Wedding App Service Worker
const CACHE_NAME = 'wedding-app-v1';
const urlsToCache = [
    '/',
    '/static/wedding/css/styles.css',
    '/static/wedding/css/responsive.css',
    '/static/wedding/css/table_map_responsive.css',
    '/static/wedding/js/app.js',
    '/static/wedding/js/table_map_leaflet.js',
    'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/4.6.2/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/4.6.2/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Caching wedding app resources');
                return cache.addAll(urlsToCache);
            })
            .catch((error) => {
                console.log('Cache failed:', error);
            })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
    // Skip cross-origin requests and non-GET requests
    if (!event.request.url.startsWith(self.location.origin) || event.request.method !== 'GET') {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                if (response) {
                    return response;
                }

                return fetch(event.request).then((response) => {
                    // Don't cache invalid responses
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Clone the response
                    const responseToCache = response.clone();

                    // Cache static assets and important pages
                    const url = event.request.url;
                    const shouldCache = (
                        url.includes('/static/') ||
                        url.includes('/media/') ||
                        url.match(/\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf)$/i) ||
                        url.endsWith('/') ||
                        url.includes('/gallery/') ||
                        url.includes('/table-finder/') ||
                        url.includes('/schedule/') ||
                        url.includes('/menu/')
                    );

                    if (shouldCache) {
                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(event.request, responseToCache);
                            });
                    }

                    return response;
                }).catch(() => {
                    // If both cache and network fail, provide fallback
                    if (event.request.destination === 'document') {
                        return caches.match('/');
                    }
                    
                    // For images, provide a placeholder
                    if (event.request.destination === 'image') {
                        return new Response(
                            '<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#f5f0e8"/><text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#8b6f47">Zdjęcie niedostępne</text></svg>',
                            {
                                headers: {
                                    'Content-Type': 'image/svg+xml'
                                }
                            }
                        );
                    }
                });
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Background sync for photo uploads (when online again)
self.addEventListener('sync', (event) => {
    if (event.tag === 'photo-upload') {
        event.waitUntil(
            // Handle queued photo uploads
            handlePhotoUploadSync()
        );
    }
});

async function handlePhotoUploadSync() {
    // This would handle any queued photo uploads when connection is restored
    try {
        // Get queued uploads from IndexedDB or localStorage
        // Process and upload them
        console.log('Processing queued photo uploads');
    } catch (error) {
        console.log('Background sync failed:', error);
    }
}

// Push notifications (if enabled in future)
self.addEventListener('push', (event) => {
    if (!event.data) return;

    const data = event.data.json();
    const title = data.title || 'Wesele';
    const options = {
        body: data.body || 'Nowe zdjęcie zostało dodane!',
        icon: '/static/wedding/images/icon-192.png',
        badge: '/static/wedding/images/badge-72.png',
        tag: 'wedding-notification',
        requireInteraction: true,
        actions: [
            {
                action: 'view',
                title: 'Zobacz',
                icon: '/static/wedding/images/view-icon.png'
            },
            {
                action: 'close',
                title: 'Zamknij'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/gallery/')
        );
    }
});

// Message handling for communication with main app
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// Periodic background sync (experimental)
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'update-photos') {
        event.waitUntil(
            updatePhotosCache()
        );
    }
});

async function updatePhotosCache() {
    try {
        const response = await fetch('/api/photos/?page=1');
        if (response.ok) {
            const cache = await caches.open(CACHE_NAME);
            await cache.put('/api/photos/?page=1', response);
        }
    } catch (error) {
        console.log('Failed to update photos cache:', error);
    }
}

console.log('Wedding App Service Worker loaded');