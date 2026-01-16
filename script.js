// Destination data
const destinations = [
    {
        id: 1,
        name: "Kapadokya",
        type: "mountain",
        description: "Peri bacaları ve balon turlarıyla ünlü, eşsiz doğal güzellikler sunan tarihi bölge.",
        ecoScore: 4.5,
        rating: 4.8,
        image: "https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=400&h=300&fit=crop"
    },
    {
        id: 2,
        name: "Ölüdeniz",
        type: "beach",
        description: "Turkuaz mavisi denizi ve muhteşem plajları ile çevre dostu tatil köyü.",
        ecoScore: 4.7,
        rating: 4.9,
        image: "https://images.unsplash.com/photo-1527838832700-5059252407fa?w=400&h=300&fit=crop"
    },
    {
        id: 3,
        name: "Yedigöller",
        type: "forest",
        description: "Bolu'nun incisi, yemyeşil ormanlar ve berrak göller ile doğa tutkunlarının cenneti.",
        ecoScore: 5.0,
        rating: 4.7,
        image: "https://images.unsplash.com/photo-1511497584788-876760111969?w=400&h=300&fit=crop"
    },
    {
        id: 4,
        name: "İstanbul",
        type: "city",
        description: "Tarih ve modernliğin buluştuğu, kültürel zenginliklerle dolu metropol.",
        ecoScore: 3.5,
        rating: 4.6,
        image: "https://images.unsplash.com/photo-1527838832700-5059252407fa?w=400&h=300&fit=crop"
    },
    {
        id: 5,
        name: "Pamukkale",
        type: "mountain",
        description: "Beyaz travertenleri ve termal suları ile doğal bir harika.",
        ecoScore: 4.3,
        rating: 4.7,
        image: "https://images.unsplash.com/photo-1605084924026-8efb60d6c4fd?w=400&h=300&fit=crop"
    },
    {
        id: 6,
        name: "Antalya",
        type: "beach",
        description: "Akdeniz'in incisi, muhteşem plajları ve antik kentleri ile ünlü tatil beldesi.",
        ecoScore: 4.1,
        rating: 4.8,
        image: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&h=300&fit=crop"
    },
    {
        id: 7,
        name: "Abant Gölü",
        type: "forest",
        description: "Bolu'nun doğa harikası, sakin göl manzarası ve çam ormanları.",
        ecoScore: 4.8,
        rating: 4.6,
        image: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop"
    },
    {
        id: 8,
        name: "Safranbolu",
        type: "city",
        description: "UNESCO Dünya Mirası listesinde, tarihi evleri ile otantik Osmanlı şehri.",
        ecoScore: 4.4,
        rating: 4.7,
        image: "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=400&h=300&fit=crop"
    },
    {
        id: 9,
        name: "Uludağ",
        type: "mountain",
        description: "Kış sporları ve doğa yürüyüşleri için ideal, Bursa'nın yüksek dağı.",
        ecoScore: 4.2,
        rating: 4.5,
        image: "https://images.unsplash.com/photo-1551582045-6ec9c11d8697?w=400&h=300&fit=crop"
    },
    {
        id: 10,
        name: "Çeşme",
        type: "beach",
        description: "Ege'nin gözde tatil beldesi, temiz plajları ve rüzgar sörfü imkanları.",
        ecoScore: 4.0,
        rating: 4.6,
        image: "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=300&fit=crop"
    },
    {
        id: 11,
        name: "Kaçkar Dağları",
        type: "mountain",
        description: "Doğu Karadeniz'in zirvesi, trekking ve doğa sporları cenneti.",
        ecoScore: 4.9,
        rating: 4.8,
        image: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&h=300&fit=crop"
    },
    {
        id: 12,
        name: "Ayder Yaylası",
        type: "forest",
        description: "Yeşilin her tonunu sunan, şelaleleri ve termal kaynakları ile doğa cenneti.",
        ecoScore: 4.7,
        rating: 4.7,
        image: "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=400&h=300&fit=crop"
    }
];

// Get DOM elements
const destinationsGrid = document.getElementById('destinationsGrid');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const filterBtns = document.querySelectorAll('.filter-btn');

let currentFilter = 'all';

// Type translations
const typeTranslations = {
    'mountain': 'Dağ',
    'beach': 'Sahil',
    'forest': 'Orman',
    'city': 'Şehir'
};

// Create destination card
function createDestinationCard(destination) {
    const card = document.createElement('div');
    card.className = 'destination-card';
    card.dataset.type = destination.type;
    card.dataset.name = destination.name.toLowerCase();
    
    const stars = '⭐'.repeat(Math.round(destination.rating));
    const ecoLeaves = '🍃'.repeat(Math.round(destination.ecoScore));
    
    card.innerHTML = `
        <img src="${destination.image}" alt="${destination.name}" class="card-image" onerror="this.src='https://via.placeholder.com/400x300?text=${encodeURIComponent(destination.name)}'">
        <div class="card-content">
            <h2 class="card-title">${destination.name}</h2>
            <span class="card-type">${typeTranslations[destination.type]}</span>
            <p class="card-description">${destination.description}</p>
            <div class="card-footer">
                <span class="eco-score" title="Çevre Dostu Puanı">
                    ${ecoLeaves} ${destination.ecoScore.toFixed(1)}
                </span>
                <span class="rating" title="Değerlendirme">
                    ${stars} ${destination.rating.toFixed(1)}
                </span>
            </div>
        </div>
    `;
    
    return card;
}

// Render destinations
function renderDestinations(destinationsToRender = destinations) {
    destinationsGrid.innerHTML = '';
    
    if (destinationsToRender.length === 0) {
        destinationsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 40px; color: #999;">Sonuç bulunamadı.</p>';
        return;
    }
    
    destinationsToRender.forEach(destination => {
        const card = createDestinationCard(destination);
        destinationsGrid.appendChild(card);
    });
}

// Filter destinations
function filterDestinations() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    
    let filtered = destinations;
    
    // Apply type filter
    if (currentFilter !== 'all') {
        filtered = filtered.filter(dest => dest.type === currentFilter);
    }
    
    // Apply search filter
    if (searchTerm) {
        filtered = filtered.filter(dest => 
            dest.name.toLowerCase().includes(searchTerm) ||
            dest.description.toLowerCase().includes(searchTerm)
        );
    }
    
    renderDestinations(filtered);
}

// Event listeners
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Update active state
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update filter
        currentFilter = btn.dataset.filter;
        filterDestinations();
    });
});

searchBtn.addEventListener('click', filterDestinations);

searchInput.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
        filterDestinations();
    }
});

searchInput.addEventListener('input', filterDestinations);

// Initial render
renderDestinations();
