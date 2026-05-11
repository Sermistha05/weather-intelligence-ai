# AI Weather Intelligence API

Production-ready FastAPI backend for AI Weather Intelligence system.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run the application:
```bash
uvicorn main:app --reload

or

python -m uvicorn main:app --reload
```

## Docker

Build and run:
```bash
docker build -t weather-api .
docker run -p 8000:8000 weather-api
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
