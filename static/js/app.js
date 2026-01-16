// Global variables
let currentPlans = null;
let map = null;
let markers = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadPOIs();
    setupEventListeners();
    // Set default location
    document.getElementById('startLocation').value = 'Ankara';
});

// Setup event listeners
function setupEventListeners() {
    // Travel form submission
    const travelForm = document.getElementById('travelForm');
    travelForm.addEventListener('submit', handleTravelFormSubmit);
    
    // GPS button
    const gpsBtn = document.getElementById('useGPSBtn');
    gpsBtn.addEventListener('click', useGPSLocation);
    
    // Location input geocoding
    const startLocationInput = document.getElementById('startLocation');
    const endLocationInput = document.getElementById('endLocation');
    
    startLocationInput.addEventListener('blur', () => {
        geocodeLocation(startLocationInput.value, 'start');
    });
    
    endLocationInput.addEventListener('blur', () => {
        if (endLocationInput.value) {
            geocodeLocation(endLocationInput.value, 'end');
        }
    });
    
    // Plan tabs
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const tier = this.getAttribute('data-tier');
            switchPlanTab(tier);
        });
    });
    
    // Review modal
    const modal = document.getElementById('reviewModal');
    const closeBtn = document.querySelector('.close');
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Review form submission
    const reviewForm = document.getElementById('reviewForm');
    reviewForm.addEventListener('submit', handleReviewSubmit);
}

// Use GPS to get current location
function useGPSLocation() {
    if (!navigator.geolocation) {
        showNotification('GPS tarayıcınız tarafından desteklenmiyor', 'error');
        return;
    }
    
    showNotification('GPS konumu alınıyor...', 'info');
    
    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            // Update hidden fields
            document.getElementById('startLat').value = lat;
            document.getElementById('startLng').value = lng;
            
            // Reverse geocode to get location name
            try {
                const locationName = await reverseGeocode(lat, lng);
                document.getElementById('startLocation').value = locationName;
                showNotification('GPS konumu başarıyla alındı: ' + locationName, 'success');
            } catch (error) {
                document.getElementById('startLocation').value = `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
                showNotification('Konum alındı ancak adres bulunamadı', 'info');
            }
        },
        (error) => {
            let message = 'GPS konumu alınamadı';
            if (error.code === error.PERMISSION_DENIED) {
                message = 'GPS erişim izni reddedildi';
            } else if (error.code === error.POSITION_UNAVAILABLE) {
                message = 'Konum bilgisi kullanılamıyor';
            } else if (error.code === error.TIMEOUT) {
                message = 'Konum alma zaman aşımına uğradı';
            }
            showNotification(message, 'error');
        },
        { timeout: 10000, enableHighAccuracy: true }
    );
}

// Geocode location name to coordinates
async function geocodeLocation(locationName, type) {
    if (!locationName || locationName.trim() === '') {
        return;
    }
    
    try {
        const response = await fetch('/api/geocode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                location: locationName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const lat = data.location.lat;
            const lng = data.location.lng;
            
            if (type === 'start') {
                document.getElementById('startLat').value = lat;
                document.getElementById('startLng').value = lng;
            } else {
                document.getElementById('endLat').value = lat;
                document.getElementById('endLng').value = lng;
            }
        } else {
            showNotification(data.error || `"${locationName}" için konum bulunamadı`, 'error');
        }
    } catch (error) {
        console.error('Geocoding error:', error);
        showNotification('Konum arama sırasında hata oluştu', 'error');
    }
}

// Reverse geocode coordinates to location name
async function reverseGeocode(lat, lng) {
    try {
        const response = await fetch('/api/reverse-geocode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lat: lat,
                lng: lng
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data.location_name;
        }
        
        return `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
    } catch (error) {
        console.error('Reverse geocoding error:', error);
        return `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
    }
}

// Handle travel form submission
async function handleTravelFormSubmit(e) {
    e.preventDefault();
    
    # First, geocode locations if they haven't been geocoded yet
    const startLocation = document.getElementById('startLocation').value;
    const endLocation = document.getElementById('endLocation').value;
    
    // Geocode start location if needed
    if (startLocation && startLocation.trim() && !document.getElementById('startLat').value) {
        await geocodeLocation(startLocation, 'start');
    }
    
    // Geocode end location if provided and not already geocoded
    if (endLocation && endLocation.trim() && !document.getElementById('endLat').value) {
        await geocodeLocation(endLocation, 'end');
    }
    
    const startLat = parseFloat(document.getElementById('startLat').value);
    const startLng = parseFloat(document.getElementById('startLng').value);
    const endLat = parseFloat(document.getElementById('endLat').value);
    const endLng = parseFloat(document.getElementById('endLng').value);
    const days = parseInt(document.getElementById('days').value);
    const budget = parseFloat(document.getElementById('budget').value);
    
    // Get selected preferences
    const preferences = Array.from(document.querySelectorAll('input[name="preferences"]:checked'))
        .map(cb => cb.value);
    
    // Prepare request data
    const requestData = {
        start_location: { lat: startLat, lng: startLng },
        days: days,
        budget: budget,
        preferences: preferences
    };
    
    // Add end location if provided
    if (endLat && endLng) {
        requestData.end_location = { lat: endLat, lng: endLng };
    }
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<span class="loading"></span> Plan Oluşturuluyor...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/api/plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentPlans = data.plans;
            displayPlans(data.plans);
            
            // Scroll to results
            document.getElementById('resultsSection').scrollIntoView({ 
                behavior: 'smooth' 
            });
        } else {
            showNotification('Hata: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Bir hata oluştu: ' + error.message, 'error');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Display travel plans
function displayPlans(plans) {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'block';
    
    // Display the basic plan by default
    switchPlanTab('basic');
}

// Switch between plan tabs
function switchPlanTab(tier) {
    if (!currentPlans || !currentPlans[tier]) return;
    
    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tier') === tier) {
            btn.classList.add('active');
        }
    });
    
    // Display plan content
    const plan = currentPlans[tier];
    displayPlanContent(plan);
    
    // Update map
    updateMap(plan);
}

// Display plan content
function displayPlanContent(plan) {
    const planContent = document.getElementById('planContent');
    
    const budgetStatusClass = plan.fits_budget ? 'fits' : 'exceeds';
    const budgetStatusText = plan.fits_budget ? '✓ Bütçe içinde' : '✗ Bütçe aşımı';
    
    let html = `
        <div class="plan-header">
            <h3>${plan.tier_name}</h3>
            <div class="cost-info">
                <div class="cost-item">
                    <div>Tahmini Maliyet</div>
                    <strong>${plan.estimated_cost.toLocaleString('tr-TR')} ₺</strong>
                </div>
                <div class="cost-item">
                    <div>Minimum Maliyet</div>
                    <strong>${plan.min_cost.toLocaleString('tr-TR')} ₺</strong>
                </div>
                <div class="cost-item">
                    <div>Maksimum Maliyet</div>
                    <strong>${plan.max_cost.toLocaleString('tr-TR')} ₺</strong>
                </div>
            </div>
            <div class="budget-status ${budgetStatusClass}">
                ${budgetStatusText}
            </div>
        </div>
        
        <div class="itinerary">
            <h3>Gün Gün Plan</h3>
    `;
    
    plan.itinerary.forEach(day => {
        html += `
            <div class="day-card">
                <div class="day-header">
                    <h4>Gün ${day.day} - ${day.date}</h4>
                </div>
        `;
        
        // Activities
        if (day.activities && day.activities.length > 0) {
            day.activities.forEach(activity => {
                html += `
                    <div class="activity">
                        <h5>${activity.name}</h5>
                        <p>${activity.description}</p>
                        <div class="activity-details">
                            <span>⏱️ ${activity.duration} saat</span>
                            <span>💰 ${activity.cost.toLocaleString('tr-TR')} ₺</span>
                            <span>🏷️ ${getCategoryName(activity.category)}</span>
                        </div>
                    </div>
                `;
            });
        }
        
        // Accommodation
        if (day.accommodation) {
            html += `
                <div class="accommodation">
                    <strong>🏨 Konaklama:</strong> ${day.accommodation.name} 
                    (${day.accommodation.cost_per_night.toLocaleString('tr-TR')} ₺)
                </div>
            `;
        }
        
        // Food cost
        if (day.food_cost) {
            html += `
                <div class="activity-details" style="margin-top: 10px;">
                    <span>🍽️ Yemek: ${day.food_cost.toLocaleString('tr-TR')} ₺</span>
                </div>
            `;
        }
        
        html += `
                <div class="day-cost">
                    Günlük Toplam: ${day.daily_cost.toLocaleString('tr-TR')} ₺
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    
    planContent.innerHTML = html;
}

// Update map with plan route
function updateMap(plan) {
    // Initialize map if not already done
    if (!map) {
        map = L.map('map').setView([39.9334, 32.8597], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    }
    
    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    // Add markers for each activity location
    const bounds = [];
    
    plan.itinerary.forEach(day => {
        if (day.activities) {
            day.activities.forEach(activity => {
                if (activity.location) {
                    const marker = L.marker([activity.location.lat, activity.location.lng])
                        .addTo(map)
                        .bindPopup(`
                            <strong>${activity.name}</strong><br>
                            ${activity.description}<br>
                            💰 ${activity.cost.toLocaleString('tr-TR')} ₺
                        `);
                    
                    markers.push(marker);
                    bounds.push([activity.location.lat, activity.location.lng]);
                }
            });
        }
    });
    
    // Fit map to show all markers
    if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [50, 50] });
    }
}

// Get category name in Turkish
function getCategoryName(category) {
    const categories = {
        'nature': 'Doğa',
        'culture': 'Kültür',
        'gastronomy': 'Gastronomi',
        'adventure': 'Macera',
        'history': 'Tarih'
    };
    return categories[category] || category;
}

// Load and display POIs
async function loadPOIs() {
    try {
        const response = await fetch('/api/pois');
        const data = await response.json();
        
        if (data.success) {
            displayPOIs(data.pois);
        }
    } catch (error) {
        console.error('POI yüklenirken hata:', error);
    }
}

// Display POIs in grid
function displayPOIs(pois) {
    const poiList = document.getElementById('poiList');
    
    let html = '';
    pois.forEach(poi => {
        html += `
            <div class="poi-card">
                <div class="poi-content">
                    <h3>${poi.name}</h3>
                    <span class="poi-category">${getCategoryName(poi.category)}</span>
                    <p class="poi-description">${poi.description}</p>
                    <div class="poi-info">
                        <div class="poi-rating">
                            ⭐ ${poi.rating}
                        </div>
                        <div class="poi-actions">
                            <button onclick="openReviewModal(${poi.id})">Yorum Yap</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    poiList.innerHTML = html;
}

// Open review modal
function openReviewModal(poiId) {
    document.getElementById('reviewPoiId').value = poiId;
    document.getElementById('reviewModal').style.display = 'block';
}

// Handle review form submission
async function handleReviewSubmit(e) {
    e.preventDefault();
    
    const poiId = document.getElementById('reviewPoiId').value;
    const rating = document.getElementById('rating').value;
    const comment = document.getElementById('comment').value;
    
    try {
        const response = await fetch('/api/review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                poi_id: poiId,
                rating: rating,
                comment: comment
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Yorumunuz başarıyla gönderildi!', 'success');
            document.getElementById('reviewModal').style.display = 'none';
            document.getElementById('reviewForm').reset();
        } else {
            showNotification('Hata: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Bir hata oluştu: ' + error.message, 'error');
    }
}

// Show notification message
function showNotification(message, type = 'info') {
    // Create notification element if it doesn't exist
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.className = 'notification';
        document.body.appendChild(notification);
    }
    
    // Set message and type
    notification.textContent = message;
    notification.className = `notification notification-${type} show`;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}
