var map = L.map('map').setView([40.7128, -74.0060], 12);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap contributors, © CARTO',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

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