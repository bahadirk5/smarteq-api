# Smarteq

Modüler ve servis katmanlı Django REST Framework projesi.

## Proje Yapısı

Proje modüler bir mimari kullanır:

```
smartеq/
├── config/                     # Proje konfigürasyonları
│   ├── settings/               # Ortam bazlı ayarlar
│   │   ├── base.py             # Temel ayarlar
│   │   ├── development.py      # Geliştirme ortamı ayarları
│   │   └── production.py       # Üretim ortamı ayarları
│   ├── urls.py                 # Ana URL yapılandırması
│   └── wsgi.py                 # WSGI yapılandırması
├── apps/                       # Modüler uygulamalar
│   ├── common/                 # Ortak araçlar ve yardımcılar
│   │   ├── models/             # Temel model sınıfları
│   │   │   └── base_model.py   # Tüm modellerin miras aldığı temel model
│   │   ├── responses.py        # Standart API yanıt formatı
│   │   └── permissions/        # Ortak izin sınıfları
│   ├── users/                  # Kullanıcı modülü
│   │   ├── models/             # Model dosyaları
│   │   ├── serializers/        # Serializer dosyaları
│   │   ├── services/           # İş mantığı servisleri
│   │   ├── repositories/       # Veritabanı işlemleri
│   │   ├── views/              # API endpoint'leri
│   │   ├── urls/               # URL yapılandırmaları
│   │   └── tests/              # Testler
│   ├── projects/               # Proje modülü
│   │   ├── models/             # Model dosyaları
│   │   ├── serializers/        # Serializer dosyaları
│   │   ├── services/           # İş mantığı servisleri
│   │   ├── repositories/       # Veritabanı işlemleri
│   │   ├── views/              # API endpoint'leri
│   │   ├── urls/               # URL yapılandırmaları
│   │   └── tests/              # Testler
│   └── inventory/              # Envanter/Üretim CRM modülü
│       ├── models/             # Model dosyaları
│       ├── serializers/        # Serializer dosyaları
│       ├── services/           # İş mantığı servisleri
│       ├── repositories/       # Veritabanı işlemleri
│       ├── views/              # API endpoint'leri
│       ├── urls/               # URL yapılandırmaları
│       ├── management/         # Yönetim komutları
│       │   └── commands/       # Özel Django komutları
│       └── tests/              # Testler
├── core/                       # Çekirdek fonksiyonellik
│   ├── exceptions/             # Özel istisna sınıfları
│   ├── middleware/             # Middleware bileşenleri
│   └── permissions/            # İzin sınıfları
├── requirements/               # Paket gereksinimleri
│   ├── base.txt                # Temel gereksinimler
│   ├── development.txt         # Geliştirme ortamı gereksinimleri
│   └── production.txt          # Üretim ortamı gereksinimleri
├── .env.example                # Örnek ortam değişkenleri
├── .gitignore                  # Git tarafından yoksayılacak dosyalar
├── docker-compose.yml          # Docker yapılandırması
└── manage.py                   # Django yönetim aracı
```

## Kurulum

### Adım 1: Projeyi Klonlama

```bash
# Projeyi klonlayın
git clone <repository-url>
# Klonlanan projeye geçin
cd smarteq/api
```

### Adım 2: Sanal Ortam Oluşturma

```bash
# Sanal ortam oluşturun
python -m venv venv

# Sanal ortamı aktifleştirin
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### Adım 3: Bağımlılıkları Yükleme

```bash
# Geliştirme ortamı gereksinimlerini yükleyin
pip install -r requirements/development.txt
```

### Adım 4: Ortam Değişkenlerini Ayarlama

```bash
# Örnek ortam değişkenleri dosyasını kopyalayın
cp .env.example .env
# .env dosyasını düzenleyin ve gerekli ayarları yapın (veritabanı bağlantısı, SECRET_KEY, vb.)
```

### Adım 5: Veritabanı Hazırlığı

#### A) Docker ile (Önerilen)

```bash
# Docker ile veritabanını başlatın
docker-compose up -d
```

#### B) Yerel Veritabanı ile

Yerel bir MySQL/PostgreSQL sunucusu kurun ve .env dosyasında bağlantı ayarlarını yapılandırın.

### Adım 6: Migrasyonları Uygulama

```bash
# Migrasyonları uygulayın
python manage.py migrate
```

### Adım 7: Örnek Verileri Yükleme (İsteğe Bağlı)

```bash
# Örnek kullanıcı verilerini yükleyin
python manage.py seed_users_data

# Örnek envanter verilerini yükleyin
python manage.py seed_inventory_data
```

### Adım 8: Geliştirme Sunucusunu Başlatma

```bash
# Geliştirme sunucusunu başlatın
python manage.py runserver
```

## Docker ile Hızlı Kurulum

```bash
# .env dosyasını oluşturun
cp .env.example .env
# .env dosyasını düzenleyin

# Docker ile başlatın
docker-compose up -d

# Migrasyonları uygulayın (Docker içinde)
docker-compose exec api python manage.py migrate

# Örnek verileri yükleyin (İsteğe Bağlı)
docker-compose exec api python manage.py seed_inventory_data
docker-compose exec api python manage.py seed_users_data
```

## Modüller ve İşlevler

### Users Modülü
- Kullanıcı yönetimi (kayıt, giriş, profil güncelleme)
- Rol ve izin yönetimi
- JWT kimlik doğrulama

### Projects Modülü
- Proje yönetimi
- Proje durumu takibi
- Proje-kullanıcı ilişkileri

### Inventory Modülü (Üretim CRM)
- Kategori yönetimi (hiyerarşik yapı)
- Ürün/Malzeme yönetimi (hammadde, ara ürün, nihai ürün)
- Ürün Ağacı (BOM) yönetimi
- Üretim Süreci takibi
- Satın Alma Siparişi kalemlerinin yönetimi

## Mimarinin Katmanları

### Model Katmanı
Veritabanı şemasını temsil eder. Her iş birimi/özellik için ayrı modeller. Tüm modeller `BaseModel` sınıfını miras alır.

### Repository Katmanı
Veritabanı işlemlerini soyutlar. Doğrudan veritabanı işlemlerini gerçekleştirir.

### Servis Katmanı
İş mantığını barındırır. Bir veya birden fazla repository kullanabilir.

### View Katmanı
API endpoint'lerini sunar. Yalnızca ilgili servis(ler)i çağırır, iş mantığı içermez. Tüm API yanıtlarını standart format ile döndürür.

## Katmanlar Arası İletişim

```
Request → View → Service → Repository → Model → Database
Response ← View ← Service ← Repository ← Model ← Database
```

## API Yanıt Formatı

Tüm API endpoint'leri tutarlı bir yanıt formatı kullanır:

```json
{
  "data": /* başarılı durumda veriler, hata durumunda null */,
  "error": /* hata durumunda hata mesajı, başarılı durumda null */,
  "status": /* HTTP durum kodu */
}
```

## Geliştirme Yaklaşımı

1. Önce modelleri tasarlayın
2. Repository katmanını oluşturun
3. Servis katmanını geliştirin
4. View ve URL yapılandırmalarını tamamlayın

## API Dokümantasyonu

API dokümantasyonuna şu adreslerden erişebilirsiniz:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`
- API Login: `http://localhost:8000/api-auth/login/`

## Sorun Giderme

### Bağımlılık Sorunları

```bash
pip install -r requirements/development.txt --upgrade
```

### Veritabanı Bağlantı Hatası

- `.env` dosyasındaki veritabanı bağlantı bilgilerinin doğru olduğundan emin olun
- Docker kullanıyorsanız, konteynerın çalıştığını doğrulayın: `docker-compose ps`

### Migrasyon Sorunları

```bash
python manage.py makemigrations
python manage.py migrate --fake-initial
```