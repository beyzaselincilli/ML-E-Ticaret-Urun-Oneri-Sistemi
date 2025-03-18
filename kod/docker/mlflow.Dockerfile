FROM python:3.9-slim

WORKDIR /mlflow

RUN pip install mlflow==2.8.1 psycopg2-binary

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "${BACKEND_STORE_URI}", \
     "--default-artifact-root", "${DEFAULT_ARTIFACT_ROOT}"] 