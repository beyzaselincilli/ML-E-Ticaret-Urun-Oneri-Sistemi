FROM apache/airflow:2.7.2-python3.9

USER root

# Sistem bağımlılıklarını kur
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Gerekli Python paketlerini kur
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# DAG'ları kopyala
COPY src/airflow/dags /opt/airflow/dags

# Airflow konfigürasyonu
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor 