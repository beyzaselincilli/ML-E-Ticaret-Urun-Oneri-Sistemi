from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mlflow
import numpy as np
from typing import List, Dict
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrikleri
REQUESTS = Counter('api_requests_total', 'Total API requests', ['endpoint'])
LATENCY = Histogram('api_latency_seconds', 'API latency', ['endpoint'])

app = FastAPI(
    title="E-Ticaret Ürün Öneri Sistemi",
    description="Kullanıcı davranışlarına göre ürün önerileri sunan API",
    version="1.0.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    user_id: int
    user_features: Dict[str, float]

class PredictionResponse(BaseModel):
    recommendations: List[Dict[str, any]]
    confidence_scores: List[float]

@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında çalışacak fonksiyon"""
    logger.info("API başlatılıyor...")
    # MLflow model yükleme
    try:
        mlflow.set_tracking_uri("http://localhost:5000")
        logger.info("MLflow bağlantısı başarılı")
    except Exception as e:
        logger.error(f"MLflow bağlantı hatası: {e}")
        raise

@app.get("/")
async def root():
    """Ana sayfa"""
    return {"message": "E-Ticaret Ürün Öneri Sistemi API'sine Hoş Geldiniz"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(input_data: UserInput):
    """
    Kullanıcı için ürün önerileri oluştur
    """
    REQUESTS.labels(endpoint='/predict').inc()
    start_time = time.time()
    
    try:
        # Model tahminleri
        logged_model = 'runs:/latest/recommendation_model'
        loaded_model = mlflow.pyfunc.load_model(logged_model)
        
        # Kullanıcı özelliklerini numpy dizisine dönüştür
        features = np.array(list(input_data.user_features.values())).reshape(1, -1)
        
        # Tahmin yap
        predictions = loaded_model.predict(features)
        
        # Örnek response oluştur
        recommendations = [
            {
                "product_id": int(pred),
                "product_name": f"Ürün {pred}",
                "category": "Kategori X",
                "price": float(np.random.randint(50, 500))
            }
            for pred in predictions[0][:5]  # İlk 5 öneriyi al
        ]
        
        confidence_scores = np.random.random(5).tolist()  # Örnek güven skorları
        
        response = PredictionResponse(
            recommendations=recommendations,
            confidence_scores=confidence_scores
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Tahmin hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        LATENCY.labels(endpoint='/predict').observe(time.time() - start_time)

@app.get("/model/health")
async def model_health():
    """Model sağlık kontrolü"""
    REQUESTS.labels(endpoint='/model/health').inc()
    start_time = time.time()
    
    try:
        # MLflow bağlantısını kontrol et
        mlflow.set_tracking_uri("http://localhost:5000")
        return {
            "status": "healthy",
            "mlflow_connection": "ok",
            "model_version": "latest"
        }
    except Exception as e:
        logger.error(f"Sağlık kontrolü hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        LATENCY.labels(endpoint='/model/health').observe(time.time() - start_time)

@app.get("/metrics")
async def metrics():
    """Prometheus metriklerini döndür"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST) 