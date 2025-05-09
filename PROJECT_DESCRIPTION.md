# SmartEQ Django API Projesi

Bu proje, SmartEQ için geliştirilmiş bir Django API uygulamasıdır.

## Proje Yapısı ve Mimarisi

### Kullanılan Teknolojiler
- Django ve Django REST Framework
- PostgreSQL (varsayılan veritabanı)
- Docker ve Docker Compose

### Ana Modüller
1. **users**: Kullanıcı yönetimi, kimlik doğrulama ve yetkilendirme
2. **inventory**: Envanter yönetimi
3. **projects**: Proje yönetimi
4. **common**: Tüm uygulamalar tarafından paylaşılan ortak işlevsellikler

### Mimari Yapı
Bu proje Domain-Driven Design prensiplerine göre yapılandırılmıştır:
- **models/**: Veri modelleri
- **repositories/**: Veritabanı işlemleri
- **services/**: İş mantığı katmanı
- **serializers/**: API veri dönüşüm katmanı
- **views/**: API endpoint'leri
- **urls/**: Routing

## Yetkilendirme Modeli
Proje, rol tabanlı bir erişim kontrol sistemi kullanmaktadır. Bu, `apps.common.permissions` modülünde tanımlanmıştır.

## Diğer Önemli Bileşenler
- Özel loglama mekanizması (`core.middleware.request_logging`)
- Ortam bazlı ayarlar (`config.settings`)

## Geliştirme Ortamı
Proje Docker ile konteynerleştirilmiş ve geliştirme ortamı `docker-compose.yml` ile yapılandırılmıştır.