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

// Load demo scenario
window.loadDemo = function(scenarioId) {
    try {
        const scenarios = {
            1: {
                startLocation: 'Ankara',
                startLat: 39.9334,
                startLng: 32.8597,
                endLocation: 'Antalya',
                endLat: 36.8969,
                endLng: 30.7133,
                days: 7,
                budget: 25000,  // 2026 gerçekçi bütçe
                preferences: ['nature', 'culture']
            },
            2: {
                startLocation: 'İstanbul, Kadıköy',
                startLat: 40.9833,
                startLng: 29.0333,
                endLocation: '',
                endLat: null,
                endLng: null,
                days: 3,
                budget: 12000,  // 2026 gerçekçi bütçe
                preferences: ['culture', 'gastronomy']
            },
            3: {
                startLocation: 'Ankara',
                startLat: 39.9334,
                startLng: 32.8597,
                endLocation: 'Nevşehir, Kapadokya',
                endLat: 38.6431,
                endLng: 34.8286,
                days: 4,
                budget: 18000,  // 2026 gerçekçi bütçe
                preferences: ['nature', 'culture']
            },
            4: {
                startLocation: 'İzmir',
                startLat: 38.4237,
                startLng: 27.1428,
                endLocation: 'Fethiye',
                endLat: 36.6542,
                endLng: 29.1256,
                days: 5,
                budget: 20000,  // 2026 gerçekçi bütçe
                preferences: ['nature', 'gastronomy']
            }
        };
        
        const scenario = scenarios[scenarioId];
        if (!scenario) {
            console.error('Scenario not found:', scenarioId);
            return;
        }
        
        console.log('Loading demo scenario:', scenarioId, scenario);
        
        // Fill form fields
        document.getElementById('startLocation').value = scenario.startLocation;
        document.getElementById('startLat').value = scenario.startLat;
        document.getElementById('startLng').value = scenario.startLng;
        document.getElementById('endLocation').value = scenario.endLocation;
        document.getElementById('endLat').value = scenario.endLat || '';
        document.getElementById('endLng').value = scenario.endLng || '';
        document.getElementById('days').value = scenario.days;
        document.getElementById('budget').value = scenario.budget;
        
        // Set preferences
        document.querySelectorAll('input[name="preferences"]').forEach(cb => {
            cb.checked = scenario.preferences.includes(cb.value);
        });
        
        // Show notification if available
        if (typeof showNotification === 'function') {
            showNotification(`Demo senaryo yüklendi: ${scenario.startLocation} ${scenario.endLocation ? '→ ' + scenario.endLocation : 'Turu'}`, 'success');
        } else {
            alert(`Demo senaryo yüklendi: ${scenario.startLocation} ${scenario.endLocation ? '→ ' + scenario.endLocation : 'Turu'}`);
        }
        
        // Scroll to form
        const form = document.getElementById('travelForm');
        if (form) {
            form.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        console.error('Error loading demo:', error);
        alert('Demo yüklenirken bir hata oluştu: ' + error.message);
    }
};

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
    
    // First, geocode locations if they haven't been geocoded yet
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
        
        console.log('API Response:', data);
        console.log('Plans:', data.plans);
        
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
    console.log('displayPlans called with:', plans);
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'block';
    
    // Initialize map
    initMap();
    
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
    console.log('displayPlanContent called with:', plan);
    const planContent = document.getElementById('planContent');
    
    if (!plan || !plan.itinerary) {
        console.error('Invalid plan data:', plan);
        planContent.innerHTML = '<p style="color: red; font-size: 18px;">Plan verisi yüklenemedi.</p>';
        return;
    }
    
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
            <h3>📅 ${plan.total_days} Günlük Detaylı Program</h3>
    `;
    
    plan.itinerary.forEach((day, index) => {
        html += `
            <div class="day-card">
                <div class="day-header">
                    <h4>🗓️ Gün ${day.day} - ${day.date}</h4>
                </div>
                
                <div class="day-content">
        `;
        
        // Activities
        if (day.activities && day.activities.length > 0) {
            html += `<div class="activities-section">
                        <h5 style="color: #2ecc71; margin-bottom: 10px;">🎯 Aktiviteler:</h5>`;
            
            day.activities.forEach((activity, actIndex) => {
                html += `
                    <div class="activity">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <span style="background: #2ecc71; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">${actIndex + 1}</span>
                            <h5 style="margin: 0; font-size: 1.2em; color: #2c3e50;">${activity.name}</h5>
                        </div>
                        <p style="margin: 10px 0; color: #666;">${activity.description}</p>
                        <div class="activity-details" style="display: flex; gap: 15px; flex-wrap: wrap; margin-top: 10px;">
                            <span style="background: #e8f5e9; padding: 5px 12px; border-radius: 20px;">⏱️ ${activity.duration} saat</span>
                            <span style="background: #fff3e0; padding: 5px 12px; border-radius: 20px;">💰 ${activity.cost.toLocaleString('tr-TR')} ₺</span>
                            <span style="background: #e3f2fd; padding: 5px 12px; border-radius: 20px;">🏷️ ${getCategoryName(activity.category)}</span>
                        </div>
                    </div>
                `;
            });
            html += `</div>`;
        } else {
            html += `<div style="padding: 15px; background: #fff3cd; border-radius: 8px; margin-bottom: 15px;">
                        <p style="margin: 0; color: #856404;">ℹ️ Bu gün için özel aktivite planlanmamış. Serbest zaman.</p>
                    </div>`;
        }
        
        // Accommodation and costs
        html += `<div class="day-summary" style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px;">`;
        
        if (day.accommodation) {
            html += `
                <div style="margin-bottom: 10px;">
                    <strong>🏨 Konaklama:</strong> ${day.accommodation.name} 
                    <span style="color: #27ae60; font-weight: bold;">(${day.accommodation.cost_per_night.toLocaleString('tr-TR')} ₺/gece)</span>
                </div>
            `;
        }
        
        if (day.food_cost) {
            html += `
                <div style="margin-bottom: 10px;">
                    <strong>🍽️ Yemek:</strong> 
                    <span style="color: #27ae60; font-weight: bold;">${day.food_cost.toLocaleString('tr-TR')} ₺</span>
                </div>
            `;
        }
        
        html += `
                <div style="margin-top: 15px; padding-top: 15px; border-top: 2px dashed #dee2e6;">
                    <strong style="font-size: 1.1em;">💵 Günlük Toplam Maliyet:</strong> 
                    <span style="color: #27ae60; font-size: 1.2em; font-weight: bold;">${day.daily_cost.toLocaleString('tr-TR')} ₺</span>
                </div>
            </div>
        `;
        
        html += `
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="plan-footer" style="background: linear-gradient(135deg, #2ecc71, #27ae60); color: white; padding: 20px; border-radius: 10px; margin-top: 20px; text-align: center;">
            <h3 style="margin: 0 0 10px 0;">🎯 Genel Toplam</h3>
            <p style="font-size: 1.5em; margin: 0; font-weight: bold;">${plan.estimated_cost.toLocaleString('tr-TR')} ₺</p>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">${plan.total_days} gün • ${budgetStatusText}</p>
        </div>
    `;
    
    planContent.innerHTML = html;
    console.log('Plan content HTML generated successfully');
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
