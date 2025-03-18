from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import mlflow
import logging
import json
import os

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DAG varsayılan argümanları
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email': ['your-email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def generate_sample_data(**context):
    """Örnek veri oluştur"""
    logger.info("Örnek veri oluşturuluyor...")
    
    # Kullanıcı özellikleri
    n_users = 1000
    n_products = 100
    
    data = {
        'user_id': np.random.randint(1, n_users + 1, size=5000),
        'product_id': np.random.randint(1, n_products + 1, size=5000),
        'user_age': np.random.randint(18, 70, size=5000),
        'user_purchase_frequency': np.random.random(size=5000),
        'product_price': np.random.randint(10, 1000, size=5000),
        'purchase_amount': np.random.randint(1, 10, size=5000)
    }
    
    df = pd.DataFrame(data)
    
    # Veriyi kaydet
    output_path = os.path.join(os.getcwd(), 'data', 'raw_data.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Veri kaydedildi: {output_path}")
    
    return output_path

def preprocess_data(**context):
    """Veri önişleme"""
    logger.info("Veri önişleme başlıyor...")
    
    # Önceki task'tan veri yolunu al
    task_instance = context['task_instance']
    data_path = task_instance.xcom_pull(task_ids='generate_data')
    
    # Veriyi oku
    df = pd.read_csv(data_path)
    
    # Önişleme adımları
    df['total_spend'] = df['product_price'] * df['purchase_amount']
    df['price_category'] = pd.qcut(df['product_price'], q=5, labels=['very_low', 'low', 'medium', 'high', 'very_high'])
    
    # Veriyi kaydet
    output_path = os.path.join(os.getcwd(), 'data', 'processed_data.csv')
    df.to_csv(output_path, index=False)
    logger.info(f"İşlenmiş veri kaydedildi: {output_path}")
    
    return output_path

def train_model(**context):
    """Model eğitimi"""
    logger.info("Model eğitimi başlıyor...")
    
    # MLflow ayarları
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("recommendation_system")
    
    # Veriyi al
    task_instance = context['task_instance']
    data_path = task_instance.xcom_pull(task_ids='preprocess_data')
    df = pd.read_csv(data_path)
    
    # Feature'ları hazırla
    features = ['user_age', 'user_purchase_frequency', 'product_price']
    target = 'purchase_amount'
    
    X = df[features]
    y = df[target]
    
    # Model eğitimi
    with mlflow.start_run():
        import lightgbm as lgb
        model = lgb.LGBMRegressor(
            objective='regression',
            num_leaves=31,
            learning_rate=0.05,
            n_estimators=100
        )
        
        model.fit(X, y)
        
        # Model metriklerini kaydet
        train_score = model.score(X, y)
        mlflow.log_metric("train_r2", train_score)
        
        # Model parametrelerini kaydet
        mlflow.log_params(model.get_params())
        
        # Modeli kaydet
        mlflow.sklearn.log_model(model, "recommendation_model")
        
        logger.info(f"Model eğitimi tamamlandı. Train R2 score: {train_score}")

# DAG tanımı
dag = DAG(
    'recommendation_training_pipeline',
    default_args=default_args,
    description='E-ticaret ürün öneri sistemi eğitim pipeline\'ı',
    schedule_interval=timedelta(days=1),
    catchup=False
)

# Task'ları oluştur
generate_data_task = PythonOperator(
    task_id='generate_data',
    python_callable=generate_sample_data,
    provide_context=True,
    dag=dag,
)

preprocess_data_task = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    provide_context=True,
    dag=dag,
)

train_model_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    provide_context=True,
    dag=dag,
)

# Task dependencies
generate_data_task >> preprocess_data_task >> train_model_task 