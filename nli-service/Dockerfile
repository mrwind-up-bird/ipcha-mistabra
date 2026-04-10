# Stage 1: Export model to ONNX (large image with torch, discarded after build)
FROM python:3.11-slim AS exporter
WORKDIR /export
COPY requirements-export.txt .
RUN pip install --no-cache-dir -r requirements-export.txt
COPY export_model.py .
RUN python export_model.py

# Stage 2: Runtime (minimal image, only onnxruntime + fastapi)
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=exporter /export/model /app/model
COPY main.py .
EXPOSE 8200
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8200"]
