FROM python:3.11.8-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0  
ENV PORT=8000     

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn app.app:app --host ${HOST} --port ${PORT}"]
