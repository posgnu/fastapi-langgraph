# fastapi-langraph

FastAPI application with LangGraph integration for streaming conversational AI agents.

## Quick Start

### 1. Setup
```bash
git clone https://github.com/posgnu/fastapi-langraph.git
cd fastapi-langraph
cp .env.example .env  # Add your OPENAI_API_KEY
poetry install
```

### 2. Run Server
```bash
poetry run uvicorn fastapi_langraph.main:app --reload
```

### 3. Test with Chat Script
```bash
# In another terminal
poetry run python scripts/chat.py
```

## API Endpoints

- **POST** `/stream` - Stream chat responses

Request:
```json
{"input": "Your message"}
```

Response: Stream of JSON objects:
```json
{"data": "Hello"}
{"data": " there!"}
```

## Testing

### Interactive Chat
```bash
poetry run python scripts/chat.py
```

### curl
```bash
curl -X POST "http://localhost:8000/stream" \
     -H "Content-Type: application/json" \
     -d '{"input": "Hello"}' --no-buffer
```

## Development
```bash
poetry run pytest       # Run tests
poetry run black .      # Format code
```
