# FastAPI RAG Application

Retrieval-Augmented Generation (RAG) system built with FastAPI, ChromaDB, and Mistral AI. This application allows you to upload PDF documents, store them in a vector database, and query them using natural language.

## Features

- 📄 **PDF Processing**: Upload and process PDF documents with automatic text extraction and chunking
- 🔍 **Vector Search**: Efficient semantic search using ChromaDB and sentence transformers
- 🤖 **AI-Powered Answers**: Get intelligent answers to your questions using Mistral AI
- 📊 **Document Management**: Track, manage, and delete uploaded documents
- 🔄 **Real-time Processing**: Asynchronous processing for optimal performance
- 📈 **Observability**: Integrated with Logfire for monitoring and debugging
- 🏗️ **Clean Architecture**: Separation of concerns with protocols and dependency injection

## Tech Stack

- **Framework**: FastAPI 0.129+
- **Python**: 3.13+
- **Vector Database**: ChromaDB 1.5+
- **AI Model**: Mistral AI (via Pydantic AI)
- **Embeddings**: Sentence Transformers 5.2+
- **PDF Processing**: PyPDF 6.7+
- **Monitoring**: Logfire 4.23+
- **Package Manager**: UV

## Project Structure

```
fastapi_rag/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── routes.py            # API endpoints
│   ├── schemas.py           # Pydantic models for requests/responses
│   ├── dtos.py              # Data transfer objects
│   ├── protocols.py         # Protocol definitions (interfaces)
│   ├── pdf_processor.py     # PDF processing logic
│   ├── vector_store.py      # ChromaDB vector store implementation
│   ├── rag_service.py       # RAG service with Mistral AI
│   ├── chroma_db/           # ChromaDB persistence directory
│   └── uploads/             # Uploaded PDF files
├── test_pdf_docs/           # Sample PDF documents
├── pyproject.toml           # Project dependencies
├── uv.lock                  # Lock file for dependencies
└── README.md                # This file
```

## Installation

### Prerequisites

- Python 3.13 or higher
- UV package manager (recommended) or pip

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fastapi_rag
   ```

2. **Install dependencies**:
   
   Using UV (recommended):
   ```bash
   uv sync
   ```
   
   Using pip:
   ```bash
   pip install -e .
   ```

3. **Create a `.env` file** in the project root:
   ```env
   # Application Settings
   APP_NAME=FastAPI RAG Application
   APP_VERSION=0.1.0
   DEBUG=False
   
   # Mistral API Settings
   MISTRAL_API_KEY=your_mistral_api_key_here
   MISTRAL_MODEL=mistral-small-latest
   
   # ChromaDB Settings
   CHROMA_PERSIST_DIRECTORY=./chroma_db
   CHROMA_COLLECTION_NAME=pdf_documents
   
   # Upload Settings
   UPLOAD_DIR=./uploads
   MAX_UPLOAD_SIZE=10485760  # 10 MB in bytes
   
   # RAG Settings
   RETRIEVAL_TOP_K=5
   CONCURRENCY=10
   
   # Logfire (optional)
   LOGFIRE_TOKEN=your_logfire_token_here
   ```

4. **Get API Keys**:
   - **Mistral API Key**: Sign up at [Mistral AI](https://console.mistral.ai/)
   - **Logfire Token** (optional): Sign up at [Logfire](https://logfire.pydantic.dev/)

## Usage

### Running the Application

Start the development server:

```bash
python -m src.main
```

Or using uvicorn directly:

```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at `http://127.0.0.1:8000`

### API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### API Endpoints

#### 1. Upload PDF Document
```http
POST /api/upload
Content-Type: multipart/form-data

file: <pdf-file>
```

**Response**:
```json
{
  "message": "PDF uploaded and processed successfully",
  "filename": "document.pdf",
  "total_documents": 5
}
```

#### 2. Query Documents
```http
POST /api/query
Content-Type: application/json

{
  "question": "What is RAG?",
  "top_k": 5
}
```

**Response**:
```json
{
  "answer": "RAG stands for Retrieval-Augmented Generation...",
  "sources": [
    {
      "filename": "document.pdf",
      "chunk_index": 0,
      "text": "..."
    }
  ],
  "confidence": "high"
}
```

#### 3. Get Statistics
```http
GET /api/stats
```

**Response**:
```json
{
  "total_documents": 3,
  "total_chunks": 45,
  "unique_files": ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
}
```

#### 4. Delete Document
```http
DELETE /api/documents/{filename}
```

**Response**:
```json
{
  "message": "Document 'document.pdf' deleted successfully"
}
```

#### 5. Reset Database
```http
POST /api/reset
```

**Response**:
```json
{
  "message": "Vector database reset successfully"
}
```

#### 6. Health Check
```http
GET /api/health
```

**Response**:
```json
{
  "status": "healthy",
  "app": "FastAPI RAG Application",
  "version": "0.1.0"
}
```

## Configuration

All configuration is managed through environment variables or the `.env` file. See `src/config.py` for available settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | FastAPI RAG Application |
| `APP_VERSION` | Application version | 0.1.0 |
| `DEBUG` | Debug mode | False |
| `MISTRAL_API_KEY` | Mistral API key | (required) |
| `MISTRAL_MODEL` | Mistral model to use | mistral-small-latest |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage path | ./chroma_db |
| `CHROMA_COLLECTION_NAME` | Collection name | pdf_documents |
| `UPLOAD_DIR` | Upload directory | ./uploads |
| `MAX_UPLOAD_SIZE` | Max file size in bytes | 10485760 (10 MB) |
| `RETRIEVAL_TOP_K` | Number of chunks to retrieve | 5 |
| `CONCURRENCY` | Max concurrent requests | 10 |
| `LOGFIRE_TOKEN` | Logfire monitoring token | (optional) |

## Architecture

The application follows clean architecture principles with clear separation of concerns:

- **Protocols**: Define interfaces for services (dependency inversion)
- **Services**: Business logic implementation (RAG, PDF processing, vector store)
- **Routes**: API endpoints and request handling
- **Schemas**: Data validation and serialization
- **DTOs**: Internal data transfer objects

### Key Components

1. **PDFProcessor**: Handles PDF file upload, storage, and text extraction
2. **VectorStore**: Manages ChromaDB operations for document storage and retrieval
3. **RAGService**: Orchestrates retrieval and generation using Mistral AI
4. **Dependency Injection**: Uses FastAPI's dependency system for loose coupling

## Development

### Code Style

The project follows Python best practices:
- Type hints throughout
- Protocol-based interfaces
- Singleton pattern for services
- Async/await for I/O operations

### Adding New Features

1. Define protocols in `protocols.py`
2. Implement business logic in service files
3. Add schemas in `schemas.py`
4. Create routes in `routes.py`
5. Update configuration in `config.py` if needed

## Troubleshooting

### Common Issues

1. **ChromaDB errors**: Ensure the `chroma_db` directory has write permissions
2. **Upload failures**: Check `MAX_UPLOAD_SIZE` setting and file permissions
3. **API key errors**: Verify your Mistral API key is valid and has credits
4. **Import errors**: Ensure all dependencies are installed correctly

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Contact

[Add contact information here]

