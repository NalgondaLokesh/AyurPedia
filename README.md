# AyurPedia

AyurPedia is an AI-powered legal and regulatory assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, and Traditional Knowledge compliance. It provides expert guidance on Indian and international frameworks including the Patents Act 1970, Biological Diversity Act 2002, FSSAI Ayurveda-Aahar Regulations 2022, Traditional Knowledge Digital Library (TKDL), and the WIPO GRATK Treaty 2024.

## Features

- **Formulation Classification**: Categorize herbal products under 7 regulatory classes (Classical, Proprietary, Ayurveda-Aahar, Cosmetic, Phytopharmaceutical, etc.)
- **Patentability Analysis**: Clarify Section 3(p) restrictions against patenting traditional knowledge, novelty requirements, and synergistic bio-enhancers
- **Regulatory Frameworks**: Guidance on Indian Patents Act 1970, Biological Diversity Act 2002 (NBA approval), FSSAI regulations, and international treaties
- **AI-Powered Chat**: Interactive Q&A with citation enforcement and confidence scoring
- **RAG System**: Retrieval-Augmented Generation with jurisdiction-aware document search

## Project Structure

```
AyurPedia/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Configuration, database, LLM client
│   │   ├── ingestion/      # Document parsing, chunking, embedding
│   │   ├── rag/            # Retrieval, prompts, chains
│   │   ├── graph/          # LangGraph workflow nodes
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   ├── api/            # FastAPI endpoints
│   │   └── utils/          # Logging, validators
│   ├── scripts/            # Ingestion scripts
│   ├── main.py             # FastAPI entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables
├── frontend/               # Frontend application
└── data/                  # Source documents
```

## Backend Implementation

### Tech Stack

- **FastAPI**: Web framework for REST API
- **LangChain**: RAG and LLM orchestration
- **LangGraph**: Workflow management (optional)
- **Google Gemini**: Primary LLM (gemini-2.5-flash)
- **Cohere**: Embedding model (embed-english-v3.0)
- **Qdrant**: Vector database for document storage
- **Pydantic**: Data validation

### API Endpoints

- `POST /api/chat` - AI assistant chat with citations
- `POST /api/classify` - Formulation classification
- `GET /api/health` - Service health check

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key

# Cohere API (Embeddings)
COHERE_API_KEY=your_cohere_api_key

# LlamaParse API (Document Parsing)
LLAMAPARSE_API_KEY=your_llamaparse_api_key

# Gemini API (LLM)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

# NVIDIA NIM API (Fallback LLM - Optional)
NVIDIA_NIM_API_KEY=your_nvidia_api_key
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1/chat/completions
FALLBACK_MODEL=meta/llama-3.1-405b-instruct

# Collection Names
INDIA_COLLECTION=india_corpus
INTERNATIONAL_COLLECTION=international_corpus

# RAG Parameters
EMBEDDING_DIMENSION=1024
BATCH_SIZE=100
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
CONFIDENCE_THRESHOLD=0.7
```

## Installation

### Prerequisites

- Python 3.10+
- Qdrant server running locally or remotely
- API keys for Cohere, Gemini, and optionally LlamaParse

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Document Ingestion

To ingest legal documents into Qdrant:

```bash
cd backend
python scripts/run_ingestion.py
```

This will:
- Parse PDF documents using LlamaParse
- Chunk documents into manageable sections
- Generate embeddings using Cohere
- Store vectors in Qdrant collections

## Usage

### Chat API

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Section 3(p) of the Patents Act?",
    "jurisdiction": "India"
  }'
```

### Classification API

```bash
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{
    "formulation": "Ashwagandha Churna with honey",
    "ingredients": ["Ashwagandha", "Honey"]
  }'
```

### Health Check

```bash
curl http://localhost:8000/api/health
```

## Architecture

### RAG Pipeline

1. **Query Processing**: Input validation and sanitization
2. **Retrieval**: Jurisdiction-aware vector search in Qdrant
3. **Context Assembly**: Format retrieved documents with metadata
4. **Generation**: LLM generates answer with citations
5. **Validation**: Citations verified against retrieved documents
6. **Confidence Scoring**: Based on similarity scores and citation coverage

### Citation System

- Citations follow format: `[Source: Document Name, Section: X.Y]`
- Citations are validated against retrieved documents
- Confidence levels: High, Medium, Low based on thresholds

### Audit Logging

All interactions are logged for DPDP compliance:
- User ID (when authenticated)
- Query and jurisdiction
- Response and citations
- Confidence score
- Timestamp
- Hashed IP address

## Development

### Running Tests

```bash
cd backend
pytest
```

### Code Style

The project follows PEP 8 guidelines. Use linting tools:
```bash
black app/
flake8 app/
```

## License

This project is developed for the AyurPedia hackathon.

## Contributing

Contributions are welcome! Please follow the existing code structure and add appropriate documentation.

## Support

For issues or questions, please contact the AyurPedia team.
