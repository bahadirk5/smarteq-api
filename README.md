# Smarteq

Modüler ve servis katmanlı Django REST Framework projesi.

## Proje Yapısı

Proje modüler bir mimari kullanır:

```
smarteq/
├── config/                     # Proje konfigürasyonları
│   ├── settings/               # Ortam bazlı ayarlar
│   ├── urls.py                 # Ana URL yapılandırması
│   └── wsgi.py
├── apps/                       # Modüler uygulamalar
│   ├── common/                 # Ortak araçlar ve yardımcılar
│   └── users/                  # Kullanıcı modülü
│       ├── models/             # Model dosyaları
│       ├── serializers/        # Serializer dosyaları
│       ├── services/           # İş mantığı servisleri
│       ├── repositories/       # Veritabanı işlemleri
│       ├── views/              # API endpoint'leri
│       ├── urls/               # URL yapılandırmaları
│       └── tests/              # Testler
├── core/                       # Çekirdek fonksiyonellik
│   ├── exceptions/
│   ├── middleware/
│   └── permissions/
└── requirements/               # Paket gereksinimleri
    ├── base.txt
    ├── development.txt
    └── production.txt
```

## Kurulum

### Geliştirme Ortamı

1. Sanal ortam oluşturun:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate    # Windows
   ```

2. Gereksinimleri yükleyin:
   ```bash
   pip install -r requirements/development.txt
   ```

3. `.env` dosyasını oluşturun:
   ```bash
   cp .env.example .env
   # .env dosyasını düzenleyin
   ```

4. Veritabanını oluşturun:
   ```bash
   python manage.py migrate
   ```

5. Geliştirme sunucusunu başlatın:
   ```bash
   python manage.py runserver
   ```

### Docker ile Kurulum

1. `.env` dosyasını oluşturun:
   ```bash
   cp .env.example .env
   # .env dosyasını düzenleyin
   ```

2. Docker ve docker-compose ile başlatın:
   ```bash
   docker-compose up -d
   ```

## Mimarinin Katmanları

### Model Katmanı
Veritabanı şemasını temsil eder. Her iş birimi/özellik için ayrı modeller.

### Repository Katmanı
Veritabanı işlemlerini soyutlar. Doğrudan veritabanı işlemlerini gerçekleştirir.

### Servis Katmanı
İş mantığını barındırır. Bir veya birden fazla repository kullanabilir.

### View Katmanı
API endpoint'lerini sunar. Yalnızca ilgili servis(ler)i çağırır, iş mantığı içermez.

## Katmanlar Arası İletişim

```
Request → View → Service → Repository → Model → Database
Response ← View ← Service ← Repository ← Model ← Database
```

## Geliştirme Yaklaşımı

1. Önce modelleri tasarlayın
2. Repository katmanını oluşturun
3. Servis katmanını geliştirin
4. View ve URL yapılandırmalarını tamamlayın
5. Her katmana uygun testler yazın

## API Dokümantasyonu

API dokümantasyonuna şu adresten erişebilirsiniz:
`http://localhost:8000/docs/`