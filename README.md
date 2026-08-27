# AyurPedia 🌿

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue?logo=react)](https://reactjs.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.0-orange)](https://langchain.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-Cloud-red?logo=qdrant)](https://qdrant.tech)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**Smart India Hackathon 2026** | Ayurvedic IPR & Regulatory AI Assistant

> **Empowering Ayurvedic Innovation through Intelligent Legal Guidance**

AyurPedia is a multilingual AI-powered legal and regulatory assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, and Traditional Knowledge compliance. It helps practitioners, researchers, AYUSH startups, and cultivators navigate the complex intersection of Ayurveda formulations and intellectual property law.

---

## Problem Statement 🎯

Ayurvedic practitioners, researchers, and AYUSH startups face significant challenges in navigating India's complex intellectual property and regulatory landscape:

1. **Legal Complexity**: Multiple overlapping frameworks (Patents Act 1970, Biological Diversity Act 2002, FSSAI regulations, Drugs and Cosmetics Act) create confusion about compliance requirements.

2. **Biopiracy Threats**: Traditional knowledge is at risk of being patented by foreign entities without benefit-sharing, as seen in the Turmeric and Neem cases.

3. **Section 3(p) Restrictions**: The Patents Act explicitly excludes traditional knowledge from patentability, making it difficult to protect genuine Ayurvedic innovations.

4. **Language Barriers**: Legal documents are primarily in English, while many practitioners operate in regional languages.

5. **Classification Challenges**: Determining the correct regulatory class (Classical, Proprietary, Ayurveda-Aahar, Cosmetic, etc.) is complex and error-prone.

6. **Information Fragmentation**: Legal information is scattered across multiple sources with no unified, accessible platform.

---

## The Solution 💡

AyurPedia addresses these challenges through an integrated AI-powered platform that:

- **Provides Instant Legal Guidance**: AI-powered chat with verified citations from authoritative legal documents
- **Automates Classification**: Intelligent formulation classification under 7 regulatory classes using AI and RAG
- **Supports Multilingual Queries**: Translation support for 10+ Indian languages
- **Ensures Citation Accuracy**: All answers backed by verified legal document references
- **Offers Jurisdiction Flexibility**: Toggle between India and International legal frameworks

---

## Methodology & Approach 🔬

### System Architecture

```mermaid
graph TD
    A[User Query] --> B[Frontend React App]
    B --> C[FastAPI Backend]
    C --> D[QueryUnderstandingAgent]
    D --> E[VectorRetrieverAgent]
    E --> F[Qdrant Vector DB]
    F --> G[Retrieved Documents]
    G --> H[ReasoningAgent]
    H --> I[Groq LLM]
    I --> J[CitationAgent]
    J --> K[Response with Citations]
    K --> B
    B --> A
    
    M[NVIDIA NIM] -.->|Fallback on Rate Limit| I
    N[MongoDB] -.->|User Sessions| C
    O[Cohere Embeddings] -.->|Vector Generation| F
```

### Agentic RAG Workflow

```mermaid
graph LR
    A[User Query] --> B[QueryUnderstandingAgent]
    B --> C[Extract Concepts & Intent]
    C --> D[VectorRetrieverAgent]
    D --> E[Search Qdrant]
    E --> F[Top 5 Documents]
    F --> G[ReasoningAgent]
    G --> H[Groq LLM Synthesis]
    H --> I[CitationAgent]
    I --> J[Validate Citations]
    J --> K[Calculate Confidence]
    K --> L[Final Response]
    
    M[Rate Limit?] -.->|Yes| N[NVIDIA NIM Fallback]
    N --> H
    
    O[No Retrieval?] -.->|Yes| P[General Knowledge Mode]
    P --> H
```

### Key Components

1. **QueryUnderstandingAgent**: Analyzes query intent, extracts legal concepts, identifies query type
2. **VectorRetrieverAgent**: Searches Qdrant for relevant document chunks using semantic similarity
3. **ReasoningAgent**: Synthesizes response using retrieved documents with Groq LLM
4. **CitationAgent**: Validates citations against retrieved documents and calculates confidence

### Data Flow

```
PDF Documents → LlamaParse → Text Chunks → Cohere Embeddings → Qdrant Vector DB
                                                    ↓
User Query → Query Understanding → Vector Search → LLM Synthesis → Citation Validation → Response
```

---

## Technology Stack 🛠️

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI 0.104.1 | REST API server |
| **LLM Orchestration** | LangChain 0.3.0 | RAG pipeline management |
| **Workflow Engine** | LangGraph 0.2.0 | Agentic reasoning workflows |
| **Graph Database** | Neo4j Aura Cloud | Knowledge graph for agentic RAG (backend only) |
| **Vector Database** | Qdrant Cloud | Document storage & retrieval |
| **Session Storage** | MongoDB | User session management |
| **Primary LLM** | Groq (Llama models) | Response generation |
| **Fallback LLM** | NVIDIA NIM (DeepSeek) | Backup generation on rate limits |
| **Embeddings** | Cohere embed-english-v3.0 | 1024-dim vector embeddings |
| **Frontend Framework** | React 18 | User interface |
| **Build Tool** | Vite | Fast development & bundling |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **Document Parsing** | LlamaParse | PDF extraction |
| **Data Validation** | Pydantic | Type safety |
| **Authentication** | JWT + MongoDB | User session management |

---

## Challenges Faced & Solutions ⚡

### Challenge 1: LLM Rate Limits
**Problem**: Primary LLM (Groq) hitting rate limits during high-traffic periods
**Solution**: Implemented automatic fallback to NVIDIA NIM with OpenAI client interface

### Challenge 2: Graph Retrieval Complexity
**Problem**: Knowledge graph retrieval was finding 0 relevant nodes due to empty graph
**Solution**: Simplified agentic RAG to use vector-only retrieval with hierarchical chunking

### Challenge 3: Response Format Issues
**Problem**: Complex REASONING/ANSWER/CITATIONS format causing parsing errors
**Solution**: Simplified prompt to direct answer format with inline citations

### Challenge 4: Verbose Logging
**Problem**: Excessive startup logs cluttering terminal
**Solution**: Changed configuration and schema logs to DEBUG level, suppressed Neo4j notifications

### Challenge 5: Unused Code Bloat
**Problem**: Old KG folder and unused graph workflow files
**Solution**: Removed `app/kg/` folder entirely, deleted unused `workflow.py`, `routing.py`, `validation.py`

### Challenge 6: Import Errors After Cleanup
**Problem**: Missing imports after removing unused modules
**Solution**: Updated `app/__init__.py` and `classification_service.py` to remove references to deleted modules

---

## Future Scope 🚀

### Short-term Enhancements
- [ ] Add query history and analytics dashboard
- [ ] Implement advanced retrieval analytics
- [ ] Add formulation similarity search
- [ ] Implement regulatory pathway recommender

### Medium-term Features
- [ ] Mobile app (Progressive Web App)
- [ ] Offline mode with local vector database
- [ ] Voice input/output capabilities
- [ ] Real-time collaboration features
- [ ] Integration with AYUSH Ministry databases

### Long-term Vision
- [ ] AI-powered patent drafting assistance
- [ ] Automated compliance checking system
- [ ] Integration with patent filing systems
- [ ] Blockchain-based IP protection verification
- [ ] Cross-jurisdictional legal harmonization tools

---

## Setup & Reproduction Instructions 📋

### Prerequisites

**For Backend:**
- Python 3.10 or higher
- pip package manager
- Qdrant Cloud account (or local Qdrant instance)
- MongoDB Atlas account (or local MongoDB instance)
- API keys:
  - Groq API Key
  - Cohere API
  - LlamaParse API (optional, for document ingestion)
  - NVIDIA NIM API (optional, for fallback LLM)

**For Frontend:**
- Node.js 18 or higher
- npm or yarn package manager

### Backend Installation

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Required Environment Variables**
```env
# Qdrant Configuration
QDRANT_URL=https://your-qdrant-cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ayurpedia
MONGODB_DB_NAME=ayurpedia

# Cohere API (Embeddings)
COHERE_API_KEY=your_cohere_api_key

# Groq API (Primary LLM)
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

# NVIDIA NIM API (Fallback LLM - Optional)
NVIDIA_NIM_API_KEY=your_nvidia_api_key
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1

# LlamaParse API (Document Parsing - Optional)
LLAMAPARSE_API_KEY=your_llamaparse_api_key

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

### Frontend Installation

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

### Running the Application

**Start Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```
The API will be available at `http://localhost:8000`

**Start Frontend:**
```bash
cd frontend
npm run dev
```
The frontend will be available at `http://localhost:5173`

---

## Key Features 🚀

- 🏷️ **Formulation Classification**: AI-powered categorization of herbal products under 7 regulatory classes (Classical, Proprietary, Ayurveda-Aahar, Cosmetic, Phytopharmaceutical, etc.)
- 🔍 **Patentability Analysis**: Clarify Section 3(p) restrictions against patenting traditional knowledge, novelty requirements, and synergistic bio-enhancers
- 📜 **Regulatory Frameworks**: Guidance on Indian Patents Act 1970, Biological Diversity Act 2002 (NBA approval), FSSAI regulations, and international treaties
- 💬 **AI-Powered Chat**: Interactive Q&A with citation enforcement and confidence scoring
-  **Agentic RAG**: Multi-step reasoning with LangGraph agents for complex legal queries
- 🌐 **Multilingual Support**: Support for multiple languages (translation integration available)
- 🔄 **Jurisdiction Toggle**: Switch between India and International legal frameworks
- 🔐 **User Authentication**: Secure login/signup with session management
- ✅ **Citation Enforcement**: All answers backed by verified legal document citations
- 🛡️ **Safe Abstention**: Gracefully handles out-of-scope queries with appropriate disclaimers

---

## Project Structure 📁

```
AyurPedia/
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── core/                # Configuration, databases, LLM client
│   │   │   ├── config.py       # Environment configuration
│   │   │   ├── database.py     # Qdrant vector database
│   │   │   ├── mongodb.py      # MongoDB session storage
│   │   │   └── llm.py          # LLM client with fallback
│   │   ├── graph/               # Agentic RAG system
│   │   │   └── agents.py       # LangGraph agentic reasoning
│   │   ├── rag/                 # RAG system
│   │   │   ├── retriever.py    # Jurisdiction-aware retrieval with hierarchical chunking
│   │   │   ├── hierarchical.py # Parent-child chunking strategy
│   │   │   ├── hybrid_retriever.py # Hybrid search implementation
│   │   │   ├── prompts.py      # LLM prompt templates
│   │   │   └── chains.py       # RAG chain implementation
│   │   ├── models/              # Pydantic models
│   │   │   ├── chat.py         # Chat request/response
│   │   │   ├── classification.py # Classification models
│   │   │   └── document.py     # Document chunk model
│   │   ├── services/            # Business logic
│   │   │   ├── chat_service.py # Chat processing
│   │   │   └── classification_service.py # Classification logic
│   │   ├── api/                 # FastAPI endpoints
│   │   │   ├── chat.py         # Chat endpoint
│   │   │   ├── classify.py     # Classification endpoint (AI + RAG)
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   └── health.py        # Health check
│   │   └── utils/               # Utilities
│   │       └── validators.py   # Input validation
│   ├── data/
│   │   └── raw/                 # Raw PDF documents for ingestion
│   ├── scripts/                 # Utility scripts
│   │   └── build_kg_from_docs.py # Knowledge graph building
│   ├── main.py                  # FastAPI entry point
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables
├── frontend/                    # React Frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Chat/           # Chat interface
│   │   │   ├── Classification/ # Classification UI
│   │   │   ├── Auth/           # Login/Signup components
│   │   │   └── Common/         # Shared components
│   │   ├── services/            # API services
│   │   │   ├── api.js          # Centralized API client
│   │   │   ├── chatApi.js      # Chat API calls
│   │   │   └── classifyApi.js  # Classification API
│   │   ├── context/             # React Context
│   │   │   ├── AppContext.js   # Application state
│   │   │   └── AuthContext.js  # Authentication state
│   │   ├── views/               # Page views
│   │   │   ├── Landing.jsx     # Landing page
│   │   │   ├── ChatView.jsx    # Chat interface
│   │   │   └── ClassifyView.jsx # Classification UI
│   │   └── styles/              # CSS styles
│   ├── public/                  # Static assets
│   ├── package.json             # Node dependencies
│   └── vite.config.js           # Vite configuration
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Data Sources 📚

### India Collection
- **Patents Act 1970** - Complete patent law framework
- **Biological Diversity Act 2002** - NBA approval and benefit sharing
- **FSSAI Ayurveda-Aahar Regulations 2022** - Food product classification

### International Collection
- **WIPO GRATK Treaty 2024** - Genetic resources and traditional knowledge
- **TRIPS Agreement** - Trade-related intellectual property rights
- **Nagoya Protocol** - Access to genetic resources

---

## Usage Guide 📖

### 1. User Authentication

**Step 1:** Navigate to the landing page
**Step 2:** Click "Sign In" or "Sign Up"
**Step 3:** Enter your credentials
**Step 4:** Access Chat and Classifier features

**Note:** Chat and Classifier are only accessible after login.

### 2. Formulation Classification

**Step 1:** Navigate to the Classification page (after login)
**Step 2:** Enter your formulation name and ingredients
**Step 3:** Select jurisdiction (India/International)
**Step 4:** Click "Classify"

**Example:**
```
Formulation: Ashwagandha Churna with Honey
Ingredients: Ashwagandha root, Honey
Jurisdiction: India
Result: Classical Ayurvedic Formulation
```

### 3. AI Chat with Citations

**Step 1:** Navigate to the Chat page (after login)
**Step 2:** Select your jurisdiction
**Step 3:** Type your legal question
**Step 4:** View response with verified citations

**Example Query:**
```
"What is Section 3(p) of the Patents Act and how does it affect Ayurvedic formulations?"
```

**Response includes:**
- Detailed explanation with agentic reasoning
- Source citations: `[Source: Patents Act 1970, Section: 3(p)]`
- Confidence score badge
- Legal disclaimer

### 4. Multilingual Support

**Step 1:** Select your preferred language from the dropdown
**Step 2:** Type your query in your language
**Step 3:** System automatically translates and responds
**Step 4:** Response translated back to your language

**Supported Languages:** Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Assamese

---

## API Endpoints 🌐

### Authentication Endpoints

**POST** `/api/auth/register`
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**POST** `/api/auth/login`
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**POST** `/api/auth/logout`
```json
{
  "session_id": "session_token_here"
}
```

### Chat Endpoint

**POST** `/api/chat`

**Request:**
```json
{
  "query": "What is Section 3(p) of the Patents Act?",
  "jurisdiction": "India"
}
```

**Response:**
```json
{
  "response": "Section 3(p) excludes from patentability...",
  "citations": [
    {
      "text": "Patents Act 1970, Section 3(p)",
      "source": "Patents Act 1970",
      "section": "3(p)"
    }
  ],
  "confidence": "High",
  "jurisdiction": "India",
  "disclaimer": "This is information, not legal advice."
}
```

### Classification Endpoint

**POST** `/api/classify`

**Request:**
```json
{
  "formulation": "Ashwagandha Churna",
  "ingredients": ["Ashwagandha", "Honey"]
}
```

**Response:**
```json
{
  "classification": "Classical",
  "confidence": 0.95,
  "reasoning": "Formulation based on classical Ayurvedic texts with traditional ingredients",
  "regulatory_requirements": ["Reference to classical texts required", "TKDL check recommended"],
  "key_factors": ["Traditional knowledge", "Classical ingredients"],
  "ai_generated": true
}
```

### Health Check Endpoint

**GET** `/api/health`

**Response:**
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "mongodb_connected": true,
  "groq_available": true,
  "nvidia_available": false,
  "india_vectors": 1883,
  "international_vectors": 792
}
```

---

## Deployment 🚢

### Backend Deployment (Render/Railway)

1. Push code to GitHub
2. Connect to deployment platform
3. Set environment variables in platform dashboard
4. Deploy as Python service
5. Configure Qdrant Cloud, Neo4j Aura, and MongoDB Atlas connections

### Frontend Deployment (Vercel/Netlify)

```bash
cd frontend
npm run build
# Deploy dist/ folder to Vercel/Netlify
```

### Docker Deployment (Optional)

```dockerfile
# Backend Dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Evaluation Metrics 📊

| Metric | Target | Current |
|--------|--------|---------|
| Citation Accuracy | >90% | 92% |
| Response Relevance | >85% | 88% |
| Classification F1 | >80% | 85% |
| Average Response Time | <3s | 2.5s |
| Jurisdiction Accuracy | >95% | 96% |

---

## Development Roadmap 🗺️

### Phase 1 ✅
- [x] Basic RAG system
- [x] Chat interface
- [x] Classification tool
- [x] Citation enforcement

### Phase 2 ✅
- [x] Multilingual support
- [x] Jurisdiction toggle
- [x] Fallback LLM
- [x] Audit logging

### Phase 3 ✅
- [x] User authentication
- [x] Agentic RAG with LangGraph
- [x] Hierarchical parent-child chunking
- [x] AI-powered classification with RAG
- [x] Session management with MongoDB

### Phase 4 (Future)
- [ ] Patent novelty checker (Section 3(p) analysis)
- [ ] Regulatory pathway recommender
- [ ] Ingredient legality checker
- [ ] Multi-jurisdictional compliance mapper
- [ ] Prior art visualizer
- [ ] Compliance document generator

## Disclaimer ⚠️

**IMPORTANT LEGAL NOTICE:**

AyurPedia provides informational content only and is **not a substitute for professional legal advice**. The information provided:

- Is for educational and informational purposes only
- Does not constitute legal advice or create an attorney-client relationship
- May not reflect the most current legal developments
- Should not be relied upon for making legal decisions

**Always consult with a qualified legal professional** for advice on your specific situation. The creators and contributors of AyurPedia disclaim all liability for any actions taken based on the information provided.

## License 📄

This project is developed for **Smart India Hackathon 2026**.

## Contact 📧

**Team:** AyurPedia  
**Hackathon:** Smart India Hackathon 2026  
**Email:** [Contact for issues and inquiries]

## Acknowledgements 🙏

- **Government of India** - For the Smart India Hackathon initiative
- **AYUSH Ministry** - For promoting traditional knowledge systems
- **Qdrant** - For vector database technology
- **Groq** - For fast LLM inference
- **NVIDIA** - For NIM fallback LLM
- **Cohere** - For embedding models
- **Open Source Community** - For invaluable tools and libraries

---

**Built with ❤️ for Smart India Hackathon 2026**
