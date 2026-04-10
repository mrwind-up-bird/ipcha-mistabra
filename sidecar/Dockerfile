FROM python:3.13-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./ipcha/
CMD ["uvicorn", "ipcha.api:app", "--host", "0.0.0.0", "--port", "8100"]
