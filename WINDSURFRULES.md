# SmartEQ API - Windsurf Rules

Bu belge, SmartEQ API projesinin yapısal bütünlüğünü korumak ve tutarlılığını sağlamak için uyulması gereken kuralları içerir. Yeni modüller oluştururken veya mevcut kodu güncellerken bu kurallar kesinlikle takip edilmelidir.

## 1. Katmanlı Mimari Kuralları

### 1.1. Proje Organizasyonu
- Tüm Django uygulamaları `apps/` dizini altında gruplanmalıdır
- Konfigürasyon dosyaları `config/` dizini altında tutulmalıdır
- Yardımcı araçlar `core/` dizininde saklanmalıdır
- Statik dosyalar `staticfiles/` dizininde saklanmalıdır
- Media dosyaları `media/` dizininde saklanmalıdır

### 1.2. Uygulama İç Yapısı
Her uygulama aşağıdaki klasör yapısını takip etmelidir:
- `models/`: Veri modelleri
- `views/`: API görünümleri
- `serializers/`: Serializer sınıfları
- `services/`: İş mantığı katmanı
- `repositories/`: Veri erişim katmanı
- `urls/`: URL yönetimi
- `migrations/`: DB göç dosyaları

## 2. Kod Yazım Kuralları

### 2.1. API Endpoint Tasarımı
- Endpoint parametreleri URL ve kod içinde **aynı isimde olmalıdır** (örn: URL'de `project_id` kullanılıyorsa, kod içinde de `project_id` kullanılmalıdır, `project` değil)
- ViewSet'lerde `filterset_fields` tanımlarında tam parametre isimleri kullanılmalıdır (örn: `['project_id', 'item_id']`)
- URL path parametreleri ile query parametreleri arasında tutarlılık sağlanmalıdır
- Özel endpoint'ler için `@action` decorator kullanılmalı ve uygun `url_path` verilmelidir

### 2.2. Servis ve Repository Katmanı
- Tüm iş mantığı Service sınıflarında olmalıdır
- Tüm veritabanı erişimi Repository sınıflarında olmalıdır
- ViewSet'ler doğrudan model erişimi yapmamalı, her zaman Service katmanını kullanmalıdır

### 2.3. Hata Yönetimi
- Hata mesajları kullanıcı dostu ve anlaşılır olmalıdır
- API yanıtları `success_response` ve `error_response` fonksiyonları ile standartlaştırılmalıdır
- Her endpoint try-except bloğu içinde çalışmalı ve hatalar yakalanmalıdır

## 3. Veri Doğrulama ve Güvenlik

### 3.1. Veri Doğrulama
- Tüm giriş verileri serializer'lar üzerinden doğrulanmalıdır
- Serializer'lar API'nin ilk savunma hattıdır
- Veri dönüştürme (serileştirme, deserileştirme) kodları ViewSet'lerde değil serializer'larda olmalıdır

### 3.2. Güvenlik
- Hassas bilgiler (API anahtarları, şifreler) asla kod içine gömülmemelidir
- Çevresel değişkenler için `.env` dosyası kullanılmalıdır
- Tüm endpoint'ler için uygun izin kontrolleri yapılmalıdır

## 4. Geriye Dönük Uyumluluk

### 4.1. URL Yapısı
- Var olan URL yapıları değiştirilmemelidir
- Yeni URL'ler mevcut yapıya uygun eklenmelidir
- Kullanımdan kaldırılacak endpoint'ler için uygun bir geçiş süreci planlanmalıdır

### 4.2. Parametre İsimleri
- Parametre isimleri projenin her yerinde tutarlı olmalıdır
- Özellikle aşağıdaki durumlar için tutarlılık sağlanmalıdır:
  - `project_id`: Proje tanımlayıcısı için kullanılmalıdır (asla sadece `project` olmamalıdır)
  - `item_id`: Ürün tanımlayıcısı için kullanılmalıdır (asla sadece `item` olmamalıdır)

## 5. Dokümantasyon

### 5.1. Kod Dokümantasyonu
- Tüm sınıflar ve metodlar için docstring yazılmalıdır
- Karmaşık iş mantığı içeren bölümler için yorum satırları eklenmelidir
- TODO ve FIXME notları geçici olmalı ve mümkün olan en kısa sürede çözülmelidir

### 5.2. API Dokümantasyonu
- Tüm API endpoint'leri için açıklayıcı dokümantasyon olmalıdır
- Request ve response formatları belgelenmelidir
- Örnek kullanım senaryoları eklenmelidir

## 6. Test Kuralları

- Her yeni özellik veya değişiklik için birim testleri yazılmalıdır
- Kritik iş mantığı entegrasyon testleri ile doğrulanmalıdır
- Testler, CI/CD pipeline'ının bir parçası olmalıdır

## 7. Performans Kuralları

- N+1 sorgu problemi engellenmeli, prefetch_related ve select_related kullanılmalıdır
- Büyük veri setleri için sayfalama (pagination) kullanılmalıdır
- Uzun süren işlemler asenkron olarak çalıştırılmalıdır

## 8. Örnek Uygulama: Proje Envanter Endpoint'leri

Aşağıdaki örnek, geçmişte yaşanan bir sorun ve çözümünü göstermektedir:

### Sorun:
Proje envanter endpoint'lerinde parametre isimlerinde tutarsızlık vardı. URL'de `project_id` kullanılırken, kod içinde `project` parametresi kontrol ediliyordu.

### Çözüm:
1. `ProjectInventoryViewSet.list` metodundaki parametre kontrolü düzeltildi: `request.query_params.get('project_id')`
2. `filterset_fields` güncellendi: `['project_id', 'item_id']`
3. Özel bir endpoint eklendi: `@action(detail=False, url_path='by_project/(?P<project_id>[^/.]+)', methods=['get'])`

### URL yapıları:
- Query ile filtreleme: `/api/v1/projects/project-inventory/?project_id=uuid`
- Path ile filtreleme: `/api/v1/projects/project-inventory/by_project/uuid/`

***

Bu kurallara kesinlikle uyulmalı ve yeni geliştirmelerde mevcut mimari yapı korunmalıdır. Bu belge projenin tutarlılığını korumak ve potansiyel hataları önlemek için bir rehber olarak kullanılmalıdır.
