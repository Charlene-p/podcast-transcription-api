# Podcast Transcription API

A FastAPI application for transcribing podcast episodes.

## Setup

### Prerequisites
- Python 3.11+
- Docker
- ffmpeg

### Installation

1. Clone the repository
```bash
git clone https://github.com/your-repo/podcast-gen.git
cd podcast-gen
```

2. Create a `.env` file with the following variables:

```bash
python -m venv venv
source venv/bin/activate # Linux/Mac
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

### Run with Docker

1. Build and run with docker compose 

```bash
docker compose up -d
```

2. Stop and remove the container

```bash
docker compose down
```


## Environment Variables

Create a `.env` file:

```env
HOST=0.0.0.0
PORT=8000
OPENAI_API_KEY = your_openai_api_key

```
