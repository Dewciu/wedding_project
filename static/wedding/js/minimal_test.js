console.log('Minimal test file loaded successfully');
document.addEventListener('DOMContentLoaded', function() {
    const mapDiv = document.getElementById('wedding-map');
    if (mapDiv) {
        mapDiv.innerHTML = '<div style="background: green; color: white; padding: 20px; text-align: center; font-size: 20px; font-weight: bold;">✅ JAVASCRIPT DZIAŁA!</div>';
    }
});
