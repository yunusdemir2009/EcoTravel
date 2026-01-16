# 🌍 EcoTravel - Akıllı Gezi Planlayıcı

EcoTravel, kullanıcıların bütçelerine ve zamanlarına göre kişiselleştirilmiş seyahat planları oluşturmalarını sağlayan akıllı bir gezi planlama uygulamasıdır.

## ✨ Temel Özellikler

### 1. Konum Bazlı Planlama
- GPS veya manuel konum girişi ile başlangıç noktası belirleme
- İsteğe bağlı hedef konum seçimi
- Gidiş-dönüş veya tek yön rotalar

### 2. Bütçe ve Gün Bazlı Planlama
- Kullanıcının belirlediği bütçe ve seyahat süresine göre otomatik rota önerisi
- Minimum ve maksimum harcama tahminleri
- Gerçek zamanlı bütçe kontrolü

### 3. Üç Farklı Seviye Plan
- **Ekonomik Plan (Basic)**: En uygun fiyatlı seçenekler, hostel/pansiyon konaklaması, toplu taşıma
- **Orta Seviye Plan**: Konforlu ama ekonomik seçenekler, 3 yıldızlı oteller, araç kiralama
- **Lüks Plan**: Maksimum konfor ve deneyim, 5 yıldızlı oteller, özel araç ve şoför

### 4. Akıllı Rota Önerisi
- Rota üzerindeki gezilecek yerler (POI - Points of Interest)
- Etkinlik önerileri
- Konaklama önerileri
- Yemek ve ulaşım planlaması

### 5. Detaylı Maliyet Hesaplaması
- Ulaşım maliyetleri
- Konaklama maliyetleri
- Yemek maliyetleri
- Aktivite ve giriş ücretleri
- Gün gün maliyet dökümü

### 6. Görsel ve İnteraktif Arayüz
- Harita tabanlı gezi görünümü (Leaflet Maps)
- Gün gün plan ve harcama dökümü
- Sezgisel kullanıcı deneyimi
- Mobil uyumlu tasarım

### 7. Kullanıcı Yorumları ve Puanlamaları
- Gezilecek yerler için yorum sistemi
- Yıldız bazlı puanlama
- Topluluk geri bildirimleri

### 8. Gezi Türü Filtreleme
- Doğa gezileri
- Kültür turları
- Gastronomi deneyimleri
- Karışık planlar

## 🚀 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### Adım 1: Depoyu Klonlayın
```bash
git clone https://github.com/yunusdemir2009/EcoTravel.git
cd EcoTravel
```

### Adım 2: Gerekli Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 3: Uygulamayı Başlatın
```bash
python app.py
```

### Adım 4: Tarayıcıda Açın
Tarayıcınızda şu adresi açın: `http://localhost:5000`

## 📖 Kullanım

### 1. Başlangıç Konumu Belirleme
- Enlem ve boylam koordinatlarını girin (örn. Ankara: 39.9334, 32.8597)
- Veya GPS kullanarak otomatik konum alın

### 2. Hedef ve Parametreleri Ayarlama
- Hedef konumu girin (isteğe bağlı)
- Gün sayısını belirleyin (1-30 gün arası)
- Bütçenizi TL olarak girin
- Gezi türü tercihlerinizi seçin (doğa, kültür, gastronomi)

### 3. Plan Oluşturma
- "Plan Oluştur" butonuna tıklayın
- Sistem otomatik olarak üç farklı seviyede plan oluşturacaktır

### 4. Planları İnceleme
- Ekonomik, Orta Seviye ve Lüks planlar arasında geçiş yapın
- Gün gün aktiviteleri inceleyin
- Harita üzerinde rotayı görüntüleyin
- Maliyet detaylarını kontrol edin

### 5. Yorum ve Puanlama
- Gezilecek yerler bölümünden ilgilendiğiniz yerleri inceleyin
- "Yorum Yap" butonuna tıklayarak deneyimlerinizi paylaşın

## 🗺️ Mevcut Gezilecek Yerler

Uygulama şu popüler destinasyonları içermektedir:
- **Anıtkabir** (Ankara) - Kültür
- **Kapadokya** (Nevşehir) - Doğa
- **Efes Antik Kenti** (İzmir) - Kültür
- **Pamukkale** (Denizli) - Doğa
- **Topkapı Sarayı** (İstanbul) - Kültür
- **Ayasofya** (İstanbul) - Kültür
- **Ölüdeniz** (Fethiye) - Doğa
- **Nemrut Dağı** (Adıyaman) - Doğa

## 🏗️ Proje Yapısı

```
EcoTravel/
├── app.py                 # Flask backend uygulaması
├── requirements.txt       # Python bağımlılıkları
├── templates/
│   └── index.html        # Ana HTML şablonu
├── static/
│   ├── css/
│   │   └── style.css     # CSS stilleri
│   └── js/
│       └── app.js        # Frontend JavaScript
└── README.md             # Proje dokümantasyonu
```

## 🔧 Teknolojiler

### Backend
- **Flask**: Python web framework
- **Flask-CORS**: Cross-origin kaynak paylaşımı
- **geopy**: Coğrafi hesaplamalar ve mesafe ölçümü
- **requests**: HTTP istekleri

### Frontend
- **HTML5**: Yapı
- **CSS3**: Modern ve responsive tasarım
- **JavaScript**: İnteraktif özellikler
- **Leaflet.js**: Interaktif harita görüntüleme

## 📊 Nasıl Çalışır?

### Planlama Motoru
1. **Konum Analizi**: Başlangıç ve hedef konumları alır
2. **POI Seçimi**: Rota üzerindeki gezilecek yerleri filtreler
3. **Bütçe Optimizasyonu**: Seçilen seviyeye göre en uygun seçenekleri belirler
4. **Rota Oluşturma**: Gün gün aktivite planı hazırlar
5. **Maliyet Hesaplama**: Ulaşım, konaklama, yemek ve aktivite maliyetlerini hesaplar

### Maliyet Hesaplama
- **Ulaşım**: Kilometre başına maliyet (seviyeye göre değişir)
  - Ekonomik: 2.5 TL/km (otobüs/paylaşımlı ulaşım)
  - Orta: 4.0 TL/km (ekonomik araç kiralama)
  - Lüks: 8.0 TL/km (premium araç + şoför)
- **Konaklama**: Şehir ve seviyeye göre değişken
- **Yemek**: Günlük sabit maliyet
  - Ekonomik: 200 TL/gün
  - Orta: 400 TL/gün
  - Lüks: 800 TL/gün
- **Aktiviteler**: Her POI için özel maliyetler

## 🎯 Gelecek Geliştirmeler

- [ ] Google Maps API entegrasyonu
- [ ] Gerçek zamanlı hava durumu entegrasyonu
- [ ] Offline plan indirme özelliği
- [ ] AI destekli mevsimsel öneriler
- [ ] Kullanıcı hesapları ve kayıtlı planlar
- [ ] Sosyal paylaşım özellikleri
- [ ] Gerçek zamanlı fiyat güncellemeleri
- [ ] Daha fazla destinasyon
- [ ] Çok dilli destek

## 🤝 Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir özellik dalı oluşturun (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Dalınıza push edin (`git push origin feature/YeniOzellik`)
5. Bir Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👨‍💻 Geliştirici

**Yunus Demir**
- GitHub: [@yunusdemir2009](https://github.com/yunusdemir2009)

## 📞 İletişim

Sorularınız veya önerileriniz için bir issue açabilirsiniz.

---

**EcoTravel ile Akıllı Seyahat Edin! 🌍✈️**