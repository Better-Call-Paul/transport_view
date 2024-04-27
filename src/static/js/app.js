var map = L.map('map');

// Function to initialize the map and get user's location
function initMap() {
    map.setView([40.7128, -74.0060], 12); // Default view
    
    // Try to get the user’s location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var userLat = position.coords.latitude;
            var userLng = position.coords.longitude;
            
            // Center the map on user's current location
            map.setView([userLat, userLng], 12);
            
            // Add a marker at the user's location
            L.marker([userLat, userLng]).addTo(map)
                .bindPopup('You are here.')
                .openPopup();
                
        }, function() {
            alert('Could not get your location. Using default location.');
        });
    }

    // Set up the tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap contributors, © CARTO',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);
}

// Add a listener to get bounds when map stops moving
map.on('moveend', function() {
    var bounds = map.getBounds();
    var ne = bounds.getNorthEast(); 
    var sw = bounds.getSouthWest(); 

    console.log('North East: ', ne.lat, ne.lng);
    console.log('South West: ', sw.lat, sw.lng);
});

// Call initMap to set up the map
initMap();

var markers = {};

function updateStationsAndDashboard() {
    fetch('/api/stations')
        .then(response => response.json())
        .then(data => {
            data.forEach(station => {
                var marker = markers[station.name];
                if (marker) {
                    marker.setLatLng([station.lat, station.lon])
                          .setIcon(L.divIcon({
                              className: 'custom-marker',
                              html: `<span>$${station.price}</span>`  // Ensure HTML is simple and controlled
                          }));
                } else {
                    markers[station.name] = L.marker([station.lat, station.lon], {
                        icon: L.divIcon({
                            className: 'custom-marker',
                            html: `<span>$${station.price}</span>`  // Consistent with update
                        })
                    }).addTo(map);
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


function updateAveragePricesChart() {
    fetch('/api/average-prices')
        .then(response => response.json())
        .then(averages => {
            const chart = document.getElementById('pricesChart');
            chart.innerHTML = ''; // Clear existing content
            let maxPrice = 5; // Define maximum price for scaling bars
            
            // Create and append new bars for updated averages
            Object.entries(averages).forEach(([neighborhood, price]) => {
                const heightPercentage = (price / maxPrice) * 100; // Calculate height as a percentage of maxPrice
                const priceBox = document.createElement('div');
                priceBox.className = 'price-box';
                priceBox.style.height = `${heightPercentage}%`;

                // Adjust dynamically styling based on value
                priceBox.innerHTML = `
                    <div class="bar" style="height: ${heightPercentage}%">
                        <p>${price.toFixed(2)}</p>
                    </div>
                    <div class="neighborhood">${neighborhood}</div>
                `;
                chart.appendChild(priceBox);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Update the average prices every 3 seconds
setInterval(updateAveragePricesChart, 3000);

// Call this function to initially load the average prices chart
updateAveragePricesChart();