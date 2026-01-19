# Chat Interface

A simple chat interface to interact with the LLM API endpoint.

## Running the Chat Interface

### Option 1: Using Python's HTTP Server

```bash
cd frontend
python3 -m http.server 3000
```

Then open your browser to `http://localhost:3000`

### Option 2: Using Node.js HTTP Server

```bash
cd frontend
npx http-server -p 3000
```

Then open your browser to `http://localhost:3000`

### Option 3: Using VS Code Live Server

If you have the Live Server extension installed in VS Code:
1. Right-click on `index.html`
2. Select "Open with Live Server"

## Prerequisites

Make sure your API server is running on `http://localhost:8000`. You can start it with:

```bash
fastapi dev src/test_opik/__init__.py
```

## Features

- Clean, modern chat interface
- Real-time message sending and receiving
- Loading indicators while waiting for responses
- Error handling and display
- Automatic scrolling to latest messages
- Responsive design

## API Endpoint

The chat interface communicates with:
- **Endpoint**: `POST http://localhost:8000/llm`
- **Request Body**: `{"message": "your question here"}`
- **Response**: `{"query": "your question", "result": "LLM response"}`
