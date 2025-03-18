FROM python:3

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

COPY bin/pull-model.sh /bin/pull-model.sh
RUN chmod +x /bin/pull-model.sh

EXPOSE 8000
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["bash", "-c", "/bin/pull-model.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000"]