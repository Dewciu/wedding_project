// Simple test script
console.log('TEST: Simple script loaded');
alert('TEST: Prosty skrypt załadowany');

document.addEventListener('DOMContentLoaded', function() {
    alert('TEST: DOM ready');
    
    const mapElement = document.getElementById('wedding-map');
    if (mapElement) {
        alert('TEST: Element mapy znaleziony');
        mapElement.innerHTML = '<div style="padding: 20px; background: red; color: white;">TEST: Element mapy działa!</div>';
    } else {
        alert('TEST: Element mapy NIE znaleziony');
    }
    
    if (typeof L !== 'undefined') {
        alert('TEST: Leaflet załadowany');
        try {
            const testMap = L.map('wedding-map', {crs: L.CRS.Simple}).setView([0, 0], 0);
            alert('TEST: Mapa Leaflet utworzona pomyślnie');
        } catch (error) {
            alert('TEST ERROR: ' + error.message);
        }
    } else {
        alert('TEST: Leaflet NIE załadowany');
    }
});
