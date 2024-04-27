var map = L.map('map').setView([40.7128, -74.0060], 12);
var markers = {};

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

function updateStationsAndDashboard() {
    fetch('/api/stations')
        .then(response => response.json())
        .then(data => {
            data.forEach(station => {
                var marker = markers[station.name];
                if (marker) {
                    marker.setLatLng([station.lat, station.lon])
                        .setPopupContent(`<b>${station.name}</b><br/>Ticket Price: $${station.price}`);
                } else {
                    markers[station.name] = L.circleMarker([station.lat, station.lon], {
                        color: 'purple',
                        radius: 10,
                        fillColor: '#af52de',
                        fillOpacity: 0.8,
                    }).addTo(map)
                      .bindPopup(`<b>${station.name}</b><br/>Ticket Price: $${station.price}`);
                }
            });

            updateDashboard(data);
        })
        .catch(error => console.error('Error:', error));
}

function updateDashboard(stations) {
    var totalPrice = 0;
    stations.forEach(station => {
        totalPrice += station.price;
    });
    var averagePrice = (totalPrice / stations.length).toFixed(2);
    document.getElementById('currentSubwaysCount').textContent = stations.length + ' Subways';
    // Update any other dashboard elements as needed
}

// Update the stations and dashboard every 3 seconds
setInterval(updateStationsAndDashboard, 3000);

// Initial call to set up the station markers and dashboard
updateStationsAndDashboard();
