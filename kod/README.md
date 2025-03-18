# E-Ticaret Ürün Öneri Sistemi MLOps Pipeline

Bu proje, e-ticaret platformları için gelişmiş bir ürün öneri sistemi MLOps pipeline'ı içermektedir. Sistem, kullanıcı davranışlarını analiz ederek kişiselleştirilmiş ürün önerileri sunar.

## Proje Bileşenleri

### 1. Veri İşleme Pipeline'ı (Airflow)
- Kullanıcı etkileşim verilerinin toplanması
- Veri temizleme ve önişleme
- Feature engineering
- Günlük veri güncelleme pipeline'ı

### 2. Model Geliştirme (MLflow)
- LightGBM tabanlı öneri sistemi
- Hyperparameter optimization (Optuna)
- Model versiyonlama
- Deney takibi ve karşılaştırma

### 3. API Servisi (FastAPI)
- RESTful API endpoints
- Model serving
- Request/Response logging
- Input validation

### 4. Monitoring ve Logging
- Model performans metrikleri
- API endpoint metrikleri
- Prometheus entegrasyonu
- Hata yakalama ve raporlama

## Kurulum

1. Gerekli paketlerin kurulumu:
```bash
pip install -r requirements.txt
```

2. Ortam değişkenlerinin ayarlanması:
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

3. MLflow server'ı başlatma:
```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts --host 0.0.0.0 --port 5000
```

4. Airflow kurulumu:
```bash
airflow db init
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
airflow webserver --port 8080
airflow scheduler
```

5. API servisini başlatma:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker ile Çalıştırma

```bash
docker-compose up -d
```

## Proje Yapısı

```
├── src/
│   ├── api/                 # FastAPI uygulaması
│   ├── airflow/            # Airflow DAG'ları
│   ├── models/             # Model eğitim ve değerlendirme kodları
│   ├── data/               # Veri işleme scriptleri
│   └── monitoring/         # Monitoring araçları
├── tests/                  # Birim testleri
├── docker/                 # Docker konfigürasyonları
├── requirements.txt        # Python bağımlılıkları
└── README.md              # Proje dokümantasyonu
```

## API Endpoints

- `POST /predict`: Kullanıcı için ürün önerileri
- `GET /model/health`: Model sağlık kontrolü
- `GET /metrics`: Prometheus metrikleri

## Monitoring

- Model performans metrikleri
- API latency ve throughput
- Başarı/hata oranları
- Resource kullanımı

## Katkıda Bulunma

1. Bu repository'yi fork edin
2. Feature branch'i oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun 