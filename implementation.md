# AyurPedia Implementation Documentation

## 1. Project Overview

AyurPedia is an AI-powered multilingual legal and regulatory intelligence platform for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, and Traditional Knowledge compliance. It addresses the complex intersection of Ayurveda formulations and intellectual property law through advanced agentic RAG, patent novelty analysis, and intelligent formulation classification.

### Problem Statement
Ayurvedic practitioners, researchers, and AYUSH startups face significant challenges navigating India's complex intellectual property and regulatory landscape:
- Multiple overlapping frameworks (Patents Act 1970, Biological Diversity Act 2002, FSSAI regulations) creating compliance confusion
- Biopiracy threats where traditional knowledge risks being patented by foreign entities without benefit-sharing
- Section 3(p) restrictions under Patents Act that exclude traditional knowledge from patentability
- Language barriers with legal documents primarily in English while practitioners operate in regional languages
- Complex formulation classification requirements across 7 regulatory categories
- Fragmented information scattered across multiple sources

### Intended Users
- Ayurvedic practitioners and researchers
- AYUSH startups and entrepreneurs
- Pharmaceutical companies developing herbal products
- Legal professionals specializing in IP and regulatory compliance
- Cultivators and traditional knowledge holders

### Primary Use Cases
1. **Legal Q&A**: Ask questions about IPR, patent law, and regulatory compliance with verified citations
2. **Formulation Classification**: Classify herbal products under regulatory categories (Classical, Proprietary, Ayurveda-Aahar, Cosmetic, Phytopharmaceutical, Nutraceutical)
3. **Patent Novelty Analysis**: Check formulations for Section 3(p) compliance and detect prior art from traditional knowledge
4. **Multilingual Support**: Query and receive responses in 10+ Indian languages
5. **Jurisdiction Comparison**: Toggle between India and International legal frameworks

### Current Implementation Status
- **Implemented and Verified**: Core chat with agentic RAG, formulation classification with AI+RAG, patent novelty checker, user authentication, MongoDB persistence, hierarchical chunking with parent-child retrieval
- **Partially Implemented**: Neo4j knowledge graph (initialized but empty, running without graph retrieval)
- **Planned/Missing**: Knowledge graph population, advanced analytics dashboard, mobile app

---

## 2. System Architecture

### High-Level Architecture

AyurPedia follows a client-server architecture with a React frontend and FastAPI backend, leveraging multiple cloud services for AI/ML capabilities.

```mermaid
graph TB
    subgraph "Frontend (React)"
        UI[User Interface]
        State[React Context State]
        API[API Client Layer]
    end
    
    subgraph "Backend (FastAPI)"
        Router[API Routes]
        Auth[Authentication Service]
        ChatService[Chat Service]
        Agents[Agentic RAG Agents]
    end
    
    subgraph "AI/ML Layer"
        LLM1[Groq LLM - Primary]
        LLM2[NVIDIA NIM - Fallback]
        Embed[Cohere Embeddings]
    end
    
    subgraph "Data Layer"
        Qdrant[Qdrant Vector DB]
        MongoDB[MongoDB Atlas]
        Neo4j[Neo4j Knowledge Graph]
    end
    
    subgraph "External Services"
        LlamaParse[LlamaParse]
        Sentry[Sentry Error Tracking]
    end
    
    UI --> State
    State --> API
    API --> Router
    Router --> Auth
    Router --> ChatService
    ChatService --> Agents
    Agents --> LLM1
    Agents --> LLM2
    Agents --> Embed
    Agents --> Qdrant
    Agents --> Neo4j
    ChatService --> MongoDB
    LLM1 -.->|Rate Limit| LLM2
    Qdrant --> Embed
    MongoDB --> Auth
    ChatService --> Sentry
    Ingestion[LlamaParse Ingestion] --> Qdrant
```

### Component Responsibilities

#### Frontend
- **UI Layer**: React components for chat, classification, patent novelty checker
- **State Management**: React Context (AuthContext, ChatContext, AppContext, AgUIContext)
- **API Client**: Axios-based HTTP client with JWT authentication
- **Real-time Features**: AG-UI streaming endpoint integration via LangGraph

#### Backend
- **API Layer**: FastAPI routers with Pydantic validation
- **Business Logic**: Service layer (ChatService, AuthService)
- **Agentic AI**: LangGraph-based multi-agent workflow (QueryUnderstanding, VectorRetriever, Reasoning, Citation)
- **Data Access**: MongoDB for persistence, Qdrant for vector search, Neo4j for knowledge graph

#### AI/ML Layer
- **Primary LLM**: Groq (Llama 3.3-70B or configurable model)
- **Fallback LLM**: NVIDIA NIM (DeepSeek or configurable model)
- **Embeddings**: Cohere embed-english-v3.0 (1024-dim vectors)
- **RAG Pipeline**: Hierarchical chunking with parent-child retrieval, query expansion, relevance boosting

#### Data Layer
- **Vector Database**: Qdrant Cloud with two collections (india_corpus, international_corpus)
- **Document Database**: MongoDB Atlas for users, conversations, classifications, facilitator requests
- **Knowledge Graph**: Neo4j Aura Cloud (currently empty, optional enhancement)

---

## 3. Technology Stack

| Technology/Library | Purpose | Where Used | Essential |
|-------------------|---------|------------|-----------|
| **FastAPI 0.115.0+** | REST API server with async support | Backend API endpoints | Yes |
| **Uvicorn** | ASGI server for FastAPI | Backend server startup | Yes |
| **React 18** | Frontend UI framework | Frontend application | Yes |
| **Vite** | Build tool and dev server | Frontend development | Yes |
| **Tailwind CSS** | Utility-first CSS styling | Frontend styling | Yes |
| **LangChain 0.3.0+** | RAG pipeline management | Backend RAG system | Yes |
| **LangGraph 0.2.0+** | Agentic workflow orchestration | Backend agentic RAG | Yes |
| **Qdrant Client** | Vector database operations | Backend vector storage/retrieval | Yes |
| **Motor** | Async MongoDB driver | Backend MongoDB persistence | Yes |
| **PyMongo** | Sync MongoDB driver | Backend MongoDB fallback | Yes |
| **Pydantic 2.7+** | Data validation and settings | Backend models and config | Yes |
| **LangChain-Groq** | Groq LLM integration | Backend primary LLM | Yes |
| **LangChain-OpenAI** | OpenAI-compatible LLM integration | Backend fallback LLM (NVIDIA NIM) | Yes |
| **Cohere** | Embedding generation | Backend embeddings | Yes |
| **LlamaParse** | PDF document parsing | Backend ingestion pipeline | Yes |
| **Neo4j** | Knowledge graph database | Backend graph retrieval (optional) | No |
| **Bcrypt 4.0+** | Password hashing | Backend authentication | Yes |
| **Python-JOSE** | JWT token handling | Backend authentication | Yes |
| **Sentry SDK** | Error tracking | Backend error monitoring | No |
| **SlowAPI** | Rate limiting | Backend API protection | Yes |
| **React Router** | Client-side routing | Frontend navigation | Yes |
| **Axios** | HTTP client | Frontend API calls | Yes |
| **React Hot Toast** | Toast notifications | Frontend user feedback | Yes |
| **Lucide React** | Icon library | Frontend UI icons | Yes |
| **AG-UI LangGraph** | LangGraph streaming UI | Frontend AG-UI streaming | Yes |

---

## 4. Repository Structure

```
AyurPedia/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── api/                      # FastAPI route handlers
│   │   │   ├── chat.py              # Chat endpoint with RAG
│   │   │   ├── classify.py          # Formulation classification endpoint
│   │   │   ├── patent.py            # Patent novelty checker endpoint
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   ├── conversations.py     # Conversation history endpoints
│   │   │   ├── conversations_auth.py # Auth-protected conversation endpoints
│   │   │   ├── facilitator.py       # Human facilitator escalation
│   │   │   ├── health.py            # Health check endpoint
│   │   │   ├── ag_ui.py             # AG-UI streaming endpoint setup
│   │   │   └── __init__.py
│   │   ├── core/                     # Core infrastructure
│   │   │   ├── config.py            # Environment configuration
│   │   │   ├── database.py          # Qdrant vector database client
│   │   │   ├── mongodb.py           # MongoDB Atlas connection manager
│   │   │   ├── neo4j.py             # Neo4j knowledge graph connection
│   │   │   ├── llm.py               # LLM client with fallback
│   │   │   ├── auth.py              # JWT utilities
│   │   │   ├── rate_limit.py        # Rate limiting middleware
│   │   │   └── sentry.py            # Sentry error tracking
│   │   ├── graph/                    # Agentic RAG system
│   │   │   └── agents.py            # LangGraph agents (QueryUnderstanding, VectorRetriever, Reasoning, Citation, PatentNovelty)
│   │   ├── rag/                      # RAG pipeline
│   │   │   ├── retriever.py         # Jurisdiction-aware retrieval with hierarchical chunking
│   │   │   ├── hierarchical.py      # Parent-child chunk expansion
│   │   │   ├── hybrid_retriever.py  # Hybrid search implementation
│   │   │   ├── chunking.py          # Advanced chunking strategies
│   │   │   ├── prompts.py           # LLM prompt templates
│   │   │   └── chains.py            # RAG chain implementation
│   │   ├── models/                   # Pydantic models
│   │   │   ├── chat.py              # Chat request/response models
│   │   │   ├── classification.py    # Classification models
│   │   │   ├── patent.py            # Patent novelty models
│   │   │   ├── user.py              # User models
│   │   │   └── document.py          # Document chunk models
│   │   ├── ingestion/                # Document ingestion pipeline
│   │   │   ├── loader.py            # Document loading logic
│   │   │   ├── parser.py            # LlamaParse integration
│   │   │   ├── chunker.py           # Advanced text chunking with hierarchical strategies
│   │   │   └── embedder.py          # Cohere embedding generation
│   │   ├── services/                 # Business logic
│   │   │   ├── chat_service.py      # Chat processing logic
│   │   │   └── auth_service.py      # Authentication logic
│   │   ├── utils/                    # Utilities
│   │   │   └── validators.py        # Input validation
│   │   └── __init__.py
│   ├── data/
│   │   └── raw/                      # Raw PDF documents for ingestion
│   │       ├── patents_act_1970.pdf
│   │       ├── biological_diversity_act_2002.pdf
│   │       ├── FSSAI_Ayurveda_Aahar_Regulations_2022.pdf
│   │       ├── wipo_gratk_treaty_2024.pdf
│   │       ├── trips_agreement_official.pdf
│   │       └── nagoya_protocol_en.pdf
│   ├── scripts/                       # Utility scripts
│   │   ├── run_ingestion.py         # Document ingestion script
│   │   └── evaluate_rag.py          # RAG evaluation script
│   ├── main.py                       # FastAPI entry point
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Environment variables (not in git)
├── frontend/                         # React Frontend
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── Chat/               # Chat interface components
│   │   │   │   ├── ChatInterface.jsx
│   │   │   │   ├── AgUIChat.jsx    # AG-UI streaming chat
│   │   │   │   ├── MessageList.jsx
│   │   │   │   ├── MessageInput.jsx
│   │   │   │   ├── CitationCard.jsx
│   │   │   │   └── ConversationSidebar.jsx
│   │   │   ├── Classification/      # Classification UI
│   │   │   │   ├── ClassifierFlow.jsx
│   │   │   │   ├── ClassificationQuestion.jsx
│   │   │   │   └── ClassificationResult.jsx
│   │   │   ├── Patent/             # Patent novelty checker UI
│   │   │   │   └── PatentNoveltyChecker.jsx
│   │   │   ├── Graph/              # Knowledge graph visualization (disabled)
│   │   │   │   └── KnowledgeGraph.jsx
│   │   │   ├── Layout/             # Layout components
│   │   │   │   ├── Header.jsx
│   │   │   │   └── Footer.jsx
│   │   │   └── Common/             # Shared components
│   │   │       ├── FacilitatorModal.jsx
│   │   │       ├── ProtectedRoute.jsx
│   │   │       ├── SkeletonLoader.jsx
│   │   │       ├── ConfidenceBadge.jsx
│   │   │       ├── JurisdictionToggle.jsx
│   │   │       └── LanguageSelector.jsx
│   │   ├── context/                 # React Context
│   │   │   ├── AppContext.jsx      # Application state (language, jurisdiction)
│   │   │   ├── AuthContext.jsx     # Authentication state
│   │   │   ├── ChatContext.jsx     # Chat state management
│   │   │   └── AgUIContext.jsx     # AG-UI streaming state
│   │   ├── services/                # API services
│   │   │   ├── api.js              # Centralized API client
│   │   │   ├── chatApi.js          # Chat API calls
│   │   │   ├── classifyApi.js      # Classification API
│   │   │   └── translationApi.js   # Multilingual translation service
│   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── useChat.js
│   │   │   ├── useClassification.js
│   │   │   ├── useKeyboardShortcuts.jsx
│   │   │   ├── useReveal.js
│   │   │   └── useTranslation.js
│   │   ├── views/                   # Page views
│   │   │   ├── LandingView.jsx     # Landing page
│   │   │   ├── LoginView.jsx       # Login page
│   │   │   ├── RegisterView.jsx    # Registration page
│   │   │   ├── PrivacySettingsView.jsx
│   │   │   ├── DisclaimerView.jsx
│   │   │   ├── PrivacyView.jsx
│   │   │   ├── TermsView.jsx
│   │   │   └── GraphView.jsx       # Knowledge graph (disabled)
│   │   ├── styles/                  # CSS styles
│   │   │   ├── App.css
│   │   │   ├── Chat.css
│   │   │   └── index.css
│   │   ├── App.jsx                  # Root App component
│   │   ├── index.jsx                # Entry point
│   │   └── routes.jsx               # Route configuration
│   ├── public/                      # Static assets
│   │   ├── favicon.svg
│   │   └── manifest.json
│   ├── package.json                 # Node dependencies
│   ├── vite.config.js               # Vite configuration
│   ├── tailwind.config.js           # Tailwind configuration
│   └── postcss.config.js            # PostCSS configuration
├── .gitignore                       # Git ignore rules
├── README.md                        # Project README
└── implementation.md                # This file
```

---

## 5. Application Execution Flow

### Chat Flow (Standard)

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant ChatService
    participant AgenticRAG
    participant VectorRetriever
    participant Qdrant
    participant LLM
    participant MongoDB

    User->>Frontend: Enter query
    Frontend->>Frontend: Add user message to state
    Frontend->>Backend: POST /api/chat (query, jurisdiction, language)
    Backend->>Backend: Verify JWT token
    Backend->>ChatService: process_query()
    ChatService->>ChatService: detect_jurisdiction_mismatch()
    ChatService->>AgenticRAG: invoke(query, jurisdiction, language)
    
    AgenticRAG->>AgenticRAG: QueryUnderstandingAgent
    AgenticRAG->>VectorRetriever: search(query, jurisdiction)
    VectorRetriever->>VectorRetriever: _expand_query()
    VectorRetriever->>Qdrant: Search vector embeddings
    Qdrant-->>VectorRetriever: Retrieved child chunks
    VectorRetriever->>VectorRetriever: apply_hierarchical_retrieval()
    VectorRetriever->>Qdrant: Retrieve parent chunks
    Qdrant-->>VectorRetriever: Parent chunks with context
    VectorRetriever-->>AgenticRAG: vector_context
    
    AgenticRAG->>AgenticRAG: ReasoningAgent
    AgenticRAG->>LLM: Synthesize response with context
    LLM-->>AgenticRAG: Response with citations
    AgenticRAG->>AgenticRAG: CitationAgent
    AgenticRAG-->>ChatService: result (response, citations, confidence)
    
    ChatService->>ChatService: format_response()
    ChatService->>ChatService: add_disclaimer()
    ChatService->>MongoDB: save_message(conversation, user_msg)
    ChatService->>MongoDB: save_message(conversation, assistant_msg)
    ChatService-->>Backend: ChatResponse
    Backend-->>Frontend: ChatResponse
    Frontend->>Frontend: Add assistant message to state
    Frontend->>User: Display response with citations
```

### Chat Flow (AG-UI Streaming)

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant AgUIEndpoint
    participant LangGraph
    participant Agents
    participant LLM

    User->>Frontend: Toggle AG-UI mode
    Frontend->>Frontend: Enable AgUIChat component
    User->>Frontend: Enter query
    Frontend->>Backend: POST /api/ag-ui (SSE stream)
    Backend->>AgUIEndpoint: Handle streaming request
    AgUIEndpoint->>LangGraph: Invoke workflow with streaming
    LangGraph->>Agents: QueryUnderstandingAgent
    Agents-->>LangGraph: Query analysis
    LangGraph->>Agents: VectorRetrieverAgent
    Agents-->>LangGraph: Retrieved context
    LangGraph->>Agents: ReasoningAgent
    Agents->>LLM: Stream response
    LLM-->>Agents: Streaming tokens
    Agents-->>LangGraph: Stream events
    LangGraph-->>AgUIEndpoint: SSE events
    AgUIEndpoint-->>Frontend: TEXT_MESSAGE_CONTENT events
    Frontend->>Frontend: Append streaming tokens to UI
    Frontend->>User: Display real-time streaming response
```

### Formulation Classification Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant ClassifyEndpoint
    participant Retriever
    participant Qdrant
    participant LLM
    participant MongoDB

    User->>Frontend: Enter formulation details
    Frontend->>Backend: POST /api/classify
    Backend->>ClassifyEndpoint: classify_formulation_endpoint()
    ClassifyEndpoint->>Retriever: Search regulatory context
    Retriever->>Qdrant: Search vector embeddings
    Qdrant-->>Retriever: Regulatory documents
    Retriever-->>ClassifyEndpoint: Regulatory context
    
    ClassifyEndpoint->>LLM: AI classification with RAG context
    LLM-->>ClassifyEndpoint: Classification result
    ClassifyEndpoint->>MongoDB: save_classification()
    ClassifyEndpoint-->>Backend: ClassificationResponse
    Backend-->>Frontend: Classification result
    Frontend->>User: Display classification with confidence
```

### Patent Novelty Checker Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant PatentAgent
    participant Retriever
    participant Qdrant
    participant LLM

    User->>Frontend: Enter formulation details
    Frontend->>Backend: POST /api/patent/novelty-check
    Backend->>PatentAgent: analyze_novelty()
    PatentAgent->>PatentAgent: Analyze ingredients
    PatentAgent->>Retriever: Search prior art
    Retriever->>Qdrant: Search traditional knowledge
    Qdrant-->>Retriever: Prior art references
    Retriever-->>PatentAgent: Prior art context
    
    PatentAgent->>PatentAgent: Analyze process novelty
    PatentAgent->>PatentAgent: Analyze combination novelty
    PatentAgent->>LLM: Synthesize overall analysis
    LLM-->>PatentAgent: Section 3(p) analysis
    PatentAgent-->>Backend: PatentNoveltyResponse
    Backend-->>Frontend: Novelty analysis result
    Frontend->>User: Display novelty score and risk level
```

---

## 6. Frontend Implementation

### Pages and Routes

| Route | Component | Protected | Description |
|-------|-----------|-----------|-------------|
| `/` | LandingView | No | Landing page with project overview |
| `/login` | LoginView | No | User login page |
| `/register` | RegisterView | No | User registration page |
| `/chat` | ChatInterface | Yes | Main chat interface with agentic RAG |
| `/classify` | ClassifierFlow | Yes | Formulation classification tool |
| `/patent` | PatentNoveltyChecker | Yes | Patent novelty checker |
| `/settings` | PrivacySettingsView | Yes | User privacy settings |
| `/disclaimer` | DisclaimerView | No | Legal disclaimer page |
| `/privacy` | PrivacyView | No | Privacy policy page |
| `/terms` | TermsView | No | Terms of use page |
| `/graph` | GraphView | Yes (disabled) | Knowledge graph visualization (disabled) |

### Major Components

#### Chat Components
- **ChatInterface.jsx**: Main chat container with toolbar, classification context banner, and input area
- **AgUIChat.jsx**: AG-UI streaming chat component for real-time LangGraph streaming
- **MessageList.jsx**: Scrollable message display with citation cards
- **MessageInput.jsx**: Text input with send button, supports keyboard shortcuts
- **CitationCard.jsx**: Display individual citations with source and section references
- **ConversationSidebar.jsx**: Sidebar for conversation history (not fully implemented)

#### Classification Components
- **ClassifierFlow.jsx**: Multi-step classification wizard
- **ClassificationQuestion.jsx**: Form for entering formulation details
- **ClassificationResult.jsx**: Display classification result with confidence and reasoning

#### Patent Components
- **PatentNoveltyChecker.jsx**: Form for patent novelty analysis with result display

#### Layout Components
- **Header.jsx**: Navigation header with jurisdiction toggle, language selector, user menu
- **Footer.jsx**: Footer with links to legal pages

#### Common Components
- **FacilitatorModal.jsx**: Modal for human facilitator escalation
- **ProtectedRoute.jsx**: Route guard for authenticated routes
- **SkeletonLoader.jsx**: Loading skeleton placeholder
- **ConfidenceBadge.jsx**: Badge displaying confidence level
- **JurisdictionToggle.jsx**: Toggle between India/International/Both jurisdictions
- **LanguageSelector.jsx**: Dropdown for language selection

### State Management

#### React Context Providers
1. **AuthProvider**: Manages user authentication state
   - `user`: Current user object
   - `isAuthenticated`: Boolean authentication status
   - `login()`: Authenticate user
   - `logout()`: Log out user
   - `register()`: Register new user

2. **AppProvider**: Manages application-wide settings
   - `language`: Selected language (default: 'en')
   - `jurisdiction`: Selected jurisdiction (default: 'India')
   - `activeTab`: Current tab navigation

3. **ChatProvider**: Manages chat state
   - `messages`: Array of chat messages
   - `isLoading`: Loading state for responses
   - `conversationId`: Current conversation ID
   - `activeClassification`: Attached classification context
   - `sendMessage()`: Send message to backend
   - `clearMessages()`: Clear chat history
   - `attachClassification()`: Attach classification to chat
   - `removeClassification()`: Remove classification context

4. **AgUIProvider**: Manages AG-UI streaming state
   - `isStreaming`: Streaming status
   - `streamingMessages`: Streaming message buffer
   - `startStream()`: Start AG-UI stream
   - `stopStream()`: Stop AG-UI stream

### API Integration

#### API Client (`services/api.js`)
- Centralized Axios instance with base URL configuration
- JWT token injection via request interceptor
- Error handling with user-friendly messages
- Automatic token refresh (not fully implemented)

#### Chat API (`services/chatApi.js`)
- `sendMessage()`: POST to `/api/chat` with query, jurisdiction, language, conversationId
- `checkHealth()`: GET to `/api/health`
- `getConversation()`: GET to `/api/conversations/{id}`
- `listConversations()`: GET to `/api/conversations` with limit

#### Classification API (`services/classifyApi.js`)
- `classifyFormulation()`: POST to `/api/classify`
- `listClassifications()`: GET to `/api/classify`
- `getCategories()`: GET to `/api/classify/categories`

#### Translation API (`services/translationApi.js`)
- `translateText()`: Translation service integration
- `detectLanguage()`: Language detection

### Forms and Validation

#### Input Validation
- Backend validation via Pydantic models
- Frontend validation via HTML5 validation and custom validators
- Email validation with regex pattern
- Password strength requirements (backend)

#### Error Handling
- Global error boundary (not implemented)
- Toast notifications for success/error feedback
- API error messages displayed to user
- Retry logic for failed requests (not implemented)

### Loading States and User Feedback

#### Loading Indicators
- Skeleton loaders during initial load
- Loading spinner during chat responses
- Button disabled states during processing
- Progress indicators for classification and patent analysis

#### User Feedback
- Toast notifications for all actions
- Error messages with actionable guidance
- Confidence badges on responses
- Disclaimer messages on all legal content

---

## 7. Backend Implementation

### Application Entry Point

**File**: `backend/main.py`

The FastAPI application is initialized with:
- Lifespan management for startup/shutdown events
- CORS middleware configuration
- Rate limiting middleware
- Request logging middleware
- Global exception handlers
- Router inclusion for all API modules

Startup sequence:
1. Load configuration from environment variables
2. Initialize Sentry error tracking
3. Connect to MongoDB Atlas (with in-memory fallback)
4. Connect to Neo4j (optional, graceful degradation)
5. Initialize Qdrant vector database client
6. Initialize LLM client with fallback
7. Initialize Retriever with top_k=15
8. Initialize Agentic RAG workflow
9. Initialize ChatService
10. Setup AG-UI streaming endpoint

### API Routes and HTTP Methods

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | Root endpoint with API information | No |
| `/api/chat` | POST | Process chat query with RAG | Yes |
| `/api/ag-ui` | POST | AG-UI streaming endpoint (LangGraph) | Yes |
| `/api/conversations` | GET | List conversation history (public endpoint) | No |
| `/api/conversations/{id}` | GET | Get specific conversation (public endpoint) | No |
| `/api/conversations` | POST | Create conversation | Yes |
| `/api/conversations` | GET | List user conversations | Yes |
| `/api/conversations/{conversation_id}` | GET | Get user conversation | Yes |
| `/api/conversations/{conversation_id}/messages` | POST | Add message to conversation | Yes |
| `/api/conversations/{conversation_id}` | DELETE | Delete conversation | Yes |
| `/api/facilitator/request` | POST | Submit human facilitator ticket | Yes |
| `/api/health` | GET | Service health check | No |
| `/api/auth/register` | POST | User registration | No |
| `/api/auth/login` | POST | User login | No |
| `/api/auth/me` | GET | Get current user | Yes |
| `/api/auth/refresh` | POST | Refresh access token | No |
| `/api/auth/consent` | PUT | Update user consent | Yes |
| `/api/auth/privacy` | PUT | Update privacy settings | Yes |
| `/api/auth/me` | DELETE | Delete user account | Yes |
| `/api/classify` | POST | Formulation classification | Yes |
| `/api/classify` | GET | List classifications | Yes |
| `/api/classify/categories` | GET | Get classification categories | No |
| `/api/classify/explanation` | GET | Get AI-powered explanation | No |
| `/api/classify/test` | POST | Test classification endpoint | No |
| `/api/patent/novelty-check` | POST | Patent novelty analysis | Yes |
| `/api/patent/section3p-info` | GET | Section 3(p) information | No |
| `/api/patent/health` | GET | Patent checker health | No |

### Request and Response Formats

#### Chat Request (`ChatRequest`)
```python
{
    "query": str,                    # User query (1-1000 chars)
    "jurisdiction": str,             # "India" | "International" | "Both"
    "language": str,                 # Target language code (e.g., "en", "hi")
    "conversation_id": str,          # Optional conversation ID
    "classification": dict,          # Optional classification context
    "user_id": str                   # User ID (set by backend)
}
```

#### Chat Response (`ChatResponse`)
```python
{
    "response": str,                 # Generated response
    "citations": List[Citation],     # List of citations
    "confidence": str,               # "High" | "Medium" | "Low"
    "confidence_score": float,       # Numeric confidence (0-1)
    "disclaimer": str,               # Legal disclaimer
    "classification": str,           # Classification result
    "jurisdiction": str,             # Jurisdiction used
    "reasoning": str,                # Step-by-step reasoning (agentic RAG)
    "graph_path": List[str]          # Knowledge graph path
}
```

#### Classification Request (`ClassificationRequest`)
```python
{
    "formulation_name": str,         # Formulation name
    "formulation_description": str,  # Description
    "ingredients": List[str],        # List of ingredients
    "dosage_form": str,              # Dosage form
    "intended_use": str,             # Intended use
    "manufacturer": str,             # Manufacturer
    "additional_info": str          # Additional information
}
```

#### Classification Response (`ClassificationResponse`)
```python
{
    "classification": str,           # Category: "Classical" | "Proprietary" | etc.
    "confidence": float,             # Confidence score (0-1)
    "reasoning": str,                # Explanation
    "regulatory_requirements": List[str],
    "key_factors": List[str],
    "id": str,                       # Classification record ID
    "ai_generated": bool             # Whether AI-generated
}
```

#### Patent Novelty Request (`PatentNoveltyRequest`)
```python
{
    "formulation_name": str,         # Formulation name
    "ingredients": List[str],        # List of ingredients
    "process": str,                  # Preparation process
    "intended_use": str,             # Intended use
    "novelty_claim": str,            # Specific novelty claim
    "jurisdiction": str              # Jurisdiction for analysis
}
```

#### Patent Novelty Response (`PatentNoveltyResponse`)
```python
{
    "formulation_name": str,
    "novelty_score": float,          # Overall novelty (0-100)
    "risk_level": str,               # "High" | "Medium" | "Low"
    "component_novelty": List[ComponentNovelty],
    "prior_art": List[PriorArtReference],
    "section3p_analysis": Section3pAnalysis,
    "confidence": float,             # Analysis confidence (0-1)
    "ai_generated": bool,
    "disclaimer": str
}
```

### Business Logic and Service Layers

#### ChatService (`app/services/chat_service.py`)
- **Jurisdiction mismatch detection**: Checks if query keywords match selected jurisdiction
- **Query processing**: Delegates to agentic RAG workflow
- **Response formatting**: Converts RAG result to ChatResponse
- **Disclaimer addition**: Adds legal disclaimer to all responses
- **Conversation persistence**: Saves messages to MongoDB with user association

#### AuthService (`app/services/auth_service.py`)
- **User creation**: Creates new user with bcrypt password hashing
- **User authentication**: Verifies credentials and returns user object
- **User retrieval**: Fetches user by ID or email
- **Consent management**: Updates user consent preferences
- **Privacy settings**: Manages user privacy preferences
- **User deletion**: Deletes user and associated data

### Validation, Exceptions, and Middleware

#### Validation
- Pydantic models for all request/response schemas
- Field validation (min_length, max_length, regex patterns)
- Custom validators in `app/utils/validators.py`
- Input sanitization for security

#### Exceptions
- Global HTTP exception handler
- General exception handler for unhandled errors
- Custom error messages for different scenarios
- Logging of all exceptions

#### Middleware
- **Rate limiting**: SlowAPI-based rate limiting (configurable per minute)
- **CORS**: Cross-origin resource sharing configuration
- **Request logging**: Logs all requests and responses for debugging
- **JWT authentication**: Dependency injection for protected routes

### Authentication and Authorization

#### JWT Token Strategy
- Access tokens: 30-minute expiration (configurable)
- Refresh tokens: 7-day expiration (configurable)
- HS256 algorithm (configurable)
- Secret key from environment variable

#### User Model
```python
{
    "id": str,                       # User ID
    "email": str,                    # Email (unique)
    "full_name": str,                # Full name
    "organization": str,             # Organization
    "password_hash": str,            # Bcrypt hashed password
    "is_active": bool,               # Account status
    "consent_given": bool,           # Privacy consent
    "created_at": datetime,          # Account creation timestamp
    "privacy_settings": dict         # Privacy preferences
}
```

#### Protected Routes
- Dependency injection via `get_current_user()`
- JWT verification via `verify_token()`
- User lookup from MongoDB
- 401 Unauthorized on invalid/missing token

---

## 8. Database and Data Management

### Database Technology and Connection Configuration

#### MongoDB Atlas
- **Connection**: Async connection via Motor with sync fallback via PyMongo
- **Database**: `ayurpedia` (configurable)
- **Connection Pool**: 50 max connections, 5 min pool size
- **Indexes**: Unique on email, indexed on timestamps
- **Fallback**: In-memory storage if MongoDB unavailable

#### Qdrant Cloud
- **Connection**: QdrantClient with cloud URL and API key
- **Collections**: `india_corpus`, `international_corpus`
- **Vector Dimension**: 1024 (Cohere embed-english-v3.0)
- **Distance Metric**: Cosine similarity
- **Batch Size**: 100 (configurable)

#### Neo4j Aura
- **Connection**: Neo4j driver with URI, username, password
- **Status**: Optional - system runs without it if unavailable
- **Current State**: Connected but empty graph
- **Fallback**: Graceful degradation to vector-only retrieval

### Collections, Tables, or Models

#### MongoDB Collections

**users**
```python
{
    "_id": ObjectId,
    "id": str,                       # Unique user ID
    "email": str,                    # Unique email
    "full_name": str,
    "organization": str,
    "password_hash": str,            # Bcrypt hash
    "is_active": bool,
    "consent_given": bool,
    "created_at": datetime,
    "privacy_settings": dict
}
```

**conversations**
```python
{
    "_id": ObjectId,
    "conversation_id": str,          # Unique conversation ID
    "user_id": str,                  # Associated user ID
    "created_at": datetime,
    "updated_at": datetime,
    "jurisdiction": str,             # "India" | "International" | "Both"
    "language": str,                 # Language code
    "messages": List[dict]           # Array of message objects
}
```

**classifications**
```python
{
    "_id": ObjectId,
    "formulation_name": str,
    "formulation_description": str,
    "ingredients": List[str],
    "dosage_form": str,
    "intended_use": str,
    "manufacturer": str,
    "additional_info": str,
    "classification": str,           # Category
    "confidence": float,
    "reasoning": str,
    "regulatory_requirements": List[str],
    "key_factors": List[str],
    "ai_generated": bool,
    "created_at": datetime,
    "user_id": str
}
```

**facilitator_requests**
```python
{
    "_id": ObjectId,
    "user_id": str,
    "query": str,
    "context": dict,
    "status": str,                   # "Pending" | "In Progress" | "Resolved"
    "created_at": datetime
}
```

#### Qdrant Collections

**india_corpus** (1883 vectors)
- Parent-child hierarchical chunking
- Metadata: source, section, jurisdiction, year, chunk_id, document_type, file_name
- Hierarchy fields: chunk_type, parent_id, child_ids, hierarchy_level, chunk_index, start_char, end_char
- Indexes: chunk_type, file_name, parent_id, jurisdiction

**international_corpus** (792 vectors)
- Same schema as india_corpus
- Documents: WIPO GRATK Treaty 2024, TRIPS Agreement, Nagoya Protocol

### Important Fields and Relationships

#### Document Chunk Hierarchy
- **Parent chunks**: ~2000 characters, provide context to LLM
- **Child chunks**: ~400 characters, used for vector search
- **Relationship**: child.parent_id → parent.id, parent.child_ids → [child.id]
- **Offset tracking**: start_char, end_char for deterministic ordering

#### User-Conversation Relationship
- One user → Many conversations
- conversations.user_id → users.id
- Indexed for efficient lookup

#### Message Structure
```python
{
    "id": str,                       # Unique message ID
    "sender": str,                   # "user" | "assistant"
    "text": str,                     # Message content
    "citations": List[dict],         # Citations (assistant only)
    "confidence": str,               # Confidence level (assistant only)
    "jurisdiction": str,             # Jurisdiction used
    "disclaimer": str,              # Legal disclaimer
    "timestamp": datetime,
    "user_id": str                   # User ID
}
```

### Data Creation, Retrieval, Updates, and Deletion

#### MongoDB Operations
- **Create**: `save_message()`, `save_classification()`, `save_facilitator_request()`
- **Retrieve**: `get_conversation()`, `list_conversations()`, `list_classifications()`
- **Update**: `update_consent()`, `update_privacy_settings()`
- **Delete**: `delete_user()` (cascades to conversations)

#### Qdrant Operations
- **Create**: `upsert_chunks()` with batch processing
- **Retrieve**: `search_similar()`, `retrieve_points()`, `scroll()`
- **Update**: Upsert operation (replace existing points)
- **Delete**: `delete_collection()`, document deduplication

### Indexes, Persistence, and Migrations

#### MongoDB Indexes
- Unique index on `users.email`
- Index on `users.created_at`
- Unique index on `conversations.conversation_id`
- Index on `conversations.user_id`
- Index on `conversations.updated_at`
- Index on `classifications.created_at`
- Index on `classifications.user_id`
- Index on `facilitator_requests.created_at`
- Index on `facilitator_requests.user_id`

#### Qdrant Payload Indexes
- Keyword index on `chunk_type` (for filtering child chunks)
- Keyword index on `file_name` (for document deduplication)
- Keyword index on `parent_id` (for parent retrieval)
- Keyword index on `jurisdiction` (for jurisdiction filtering)

#### Migrations
- No formal migration system
- Indexes created on startup via `_ensure_indexes()`
- Manual schema changes require direct database operations
- In-memory fallback for development/testing

---

## 9. AI/ML and Agentic AI Implementation

### Model Names and Responsibilities

#### Primary LLM: Groq
- **Model**: Configurable via `GROQ_MODEL` (default: `llama-3.3-70b-versatile`)
- **Responsibilities**: Query understanding, response synthesis, classification, patent analysis
- **Configuration**: Temperature 0.4, max_tokens 4096
- **Fallback**: NVIDIA NIM on rate limit errors

#### Fallback LLM: NVIDIA NIM
- **Model**: Configurable via `FALLBACK_MODEL` (default: `deepseek-ai/deepseek-v4-flash-0731`)
- **Responsibilities**: Backup for primary LLM when rate limited
- **Interface**: OpenAI-compatible API via LangChain ChatOpenAI
- **Direct Access**: Direct OpenAI client for advanced features (reasoning, extra_body)

#### Embedding Model: Cohere
- **Model**: `embed-english-v3.0`
- **Dimension**: 1024
- **Responsibilities**: Query and document embeddings for vector search
- **Batch Processing**: Configurable batch size (default: 100)

### Agent Roles, Tools, and Orchestration

#### Agentic RAG Workflow (LangGraph)

**State**: `AgentState`
```python
{
    "query": str,
    "jurisdiction": str,
    "language": str,
    "query_analysis": dict,          # Query understanding results
    "vector_context": List[dict],    # Retrieved documents
    "reasoning": str,                # Step-by-step reasoning
    "response": str,                 # Final response
    "citations": List[dict],         # Validated citations
    "confidence": str,               # Confidence level
    "messages": List[BaseMessage]    # LangGraph messages channel
}
```

**Agents**:

1. **QueryUnderstandingAgent**
   - **Role**: Analyze query intent, extract legal concepts, identify query type
   - **Input**: User query, jurisdiction, language
   - **Output**: Query analysis with query_type, concepts, specific_sections, urgency
   - **LLM**: Groq or fallback
   - **Prompt**: JSON-formatted analysis with query classification

2. **GraphRetrieverAgent** (Optional)
   - **Role**: Retrieve relevant legal concepts from Neo4j knowledge graph
   - **Input**: Query, jurisdiction
   - **Output**: Graph context with nodes and relationships
   - **Database**: Neo4j (gracefully skips if unavailable)
   - **Search**: Multiple node types (Statute, Section, Concept, Framework)

3. **VectorRetrieverAgent**
   - **Role**: Retrieve detailed legal text from Qdrant vector database
   - **Input**: Query, jurisdiction
   - **Output**: Vector context with retrieved documents
   - **Database**: Qdrant with hierarchical retrieval
   - **Search**: Jurisdiction-aware with query expansion

4. **ReasoningAgent**
   - **Role**: Synthesize legal reasoning from retrieved context
   - **Input**: Query, vector context, language
   - **Output**: Reasoning, response, citations
   - **LLM**: Groq or fallback with streaming
   - **Prompt**: Direct answer format with inline citations
   - **Fallback**: Citation extraction from context if LLM fails

5. **CitationAgent**
   - **Role**: Validate citations and calculate confidence
   - **Input**: Response, citations, vector context
   - **Output**: Validated citations, confidence level
   - **Validation**: Checks citation format and source mapping

**Workflow**:
```
QueryUnderstandingAgent → VectorRetrieverAgent → ReasoningAgent → CitationAgent
```

**State Transitions**:
- QueryUnderstandingAgent: Extracts query metadata
- VectorRetrieverAgent: Populates vector_context
- ReasoningAgent: Generates response with reasoning
- CitationAgent: Validates and calculates confidence

### State Transitions and Workflow Execution

#### Agentic RAG Execution
```python
result = agentic_rag.invoke(
    query="what is act 1970?",
    jurisdiction="India",
    language="en"
)
```

#### AG-UI Streaming Execution
```python
# Backend
for event in agentic_rag.stream(
    {"query": query, "jurisdiction": jurisdiction, "language": language},
    config={"recursion_limit": 10}
):
    yield event

# Frontend
eventSource.onmessage = (event) => {
    if (event.type === 'TEXT_MESSAGE_CONTENT') {
        appendStreamingToken(event.data);
    }
}
```

### Prompt Templates and Structured Outputs

#### Query Understanding Prompt
```python
"""
Analyze this legal query for Ayurvedic IPR and patent law.

QUERY: {query}
JURISDICTION: {jurisdiction}
LANGUAGE: {language}

Provide a JSON-formatted analysis with these fields:
{
  "query_type": "classification|legal_question|comparison|procedure|general",
  "concepts": ["list of 3-5 key legal concepts"],
  "jurisdiction_match": true/false,
  "is_multi_part": true/false,
  "specific_sections": ["any specific sections mentioned like 3(p), 3(d)"],
  "urgency": "normal|high",
  "entities": ["any specific entities mentioned"]
}

Return ONLY the JSON, no other text.
"""
```

#### Reasoning Prompt
```python
"""
You are an expert legal analyst for Ayurvedic Intellectual Property law.
Answer the user's question using the retrieved document context.

USER QUERY: {query}
TARGET LANGUAGE: {language}

RETRIEVED DOCUMENTS:
{vector_summary}

SOURCE MAPPING FOR CITATIONS:
{source_mapping}

INSTRUCTIONS:
1. Provide a clear, direct answer to the user's question
2. Reference specific information from the documents using the citation format: [Source: Document Name] or [Source: Document Name, Section: X.Y]
3. Use the exact document names from the SOURCE MAPPING above
4. IMPORTANT: You MUST include at least 2-3 citations in your response using the format [Source: Document Name]
5. Format your response in {language}
6. Keep it concise but comprehensive
7. Include a brief disclaimer at the end
8. At the very end of your response, add a "References" section listing all sources cited

**References:**
- [Source: Document Name]
- [Source: Document Name, Section: X.Y]
"""
```

#### Classification Prompt
```python
"""
You are an expert in Indian Ayurvedic regulatory frameworks and intellectual property law.

{rag_context}

Formulation to Classify:
{formulation_analysis}

Classification Categories:
1. **Classical**: Traditional formulations from ancient Ayurvedic texts
2. **Proprietary**: Novel, patented, or unique formulations
3. **Ayurveda-Aahar**: Food and nutritional products (FSSAI regulations)
4. **Cosmetic**: External application products for skin, hair, beauty care
5. **Phytopharmaceutical**: Plant-based drug products with therapeutic applications
6. **Nutraceutical**: Dietary supplements with health benefits
7. **Unknown**: Cannot be determined with available information

Provide your analysis in this exact JSON format:
{
    "classification": "category_name",
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation (2-3 sentences)",
    "regulatory_requirements": ["requirement1", "requirement2"],
    "key_factors": ["factor1", "factor2"]
}

Consider: Traditional knowledge vs novelty (Section 3(p)), intended use, ingredients, regulatory framework. Keep reasoning concise.
"""
```

### Retrieval, Chunking, Embedding Generation, Reranking, and Grounding

#### Hierarchical Chunking Strategy
- **Parent chunks**: 2000 characters with 200 character overlap
- **Child chunks**: 400 characters with 100 character overlap
- **Relationship**: Child chunks are subsets of parent chunks
- **Offset tracking**: start_char, end_char for precise document mapping
- **Implementation**: `app/rag/hierarchical.py` with `expand_to_parents()`

#### Query Expansion
- **Term expansions**: Legal term mappings for better retrieval
- **Domain terms**: Contextual additions based on query analysis
- **Example**: "section 3(p)" → "section 3(p) traditional knowledge patentability novelty prior art inventive step"
- **Implementation**: `app/rag/retriever.py` with `_expand_query()`

#### Retrieval Pipeline
1. **Query expansion**: Add legal terms and domain-specific keywords
2. **Embedding generation**: Cohere embed-english-v3.0
3. **Vector search**: Qdrant similarity search with jurisdiction filtering
4. **Score boosting**: Boost results with legal sections, acts, key terms
5. **Hierarchical expansion**: Expand child chunks to parent chunks
6. **Deduplication**: Remove duplicate parent chunks
7. **Top-k selection**: Return top 15 results (configurable)

#### Relevance Boosting
- **Section numbers**: +0.1 boost for legal section references
- **Legal sources**: +0.15 boost for acts, regulations, treaties
- **Key terms**: +0.1 boost for patentability, novelty, prior art
- **Final score**: min(score * boost, 1.0)

### Knowledge-Source Ingestion and Indexing

#### Ingestion Pipeline (`scripts/run_ingestion.py`)

**Documents**:
- India: Patents Act 1970, Biological Diversity Act 2002, FSSAI Ayurveda-Aahar Regulations 2022
- International: WIPO GRATK Treaty 2024, TRIPS Agreement, Nagoya Protocol

**Process**:
1. **PDF Parsing**: LlamaParse extracts text and metadata
2. **Chunking**: Hierarchical chunking with parent-child relationships
3. **Embedding**: Cohere batch embedding generation
4. **Loading**: Qdrant upsert with deduplication
5. **Indexing**: Payload indexes for efficient filtering

**Chunker Configuration**:
- Parent chunk size: 2000 characters
- Child chunk size: 400 characters
- Chunk overlap: 100 characters
- Parent overlap: 200 characters

### Memory Management and Context Handling

#### Conversation Memory
- **Storage**: MongoDB with conversation_id and user_id
- **Persistence**: Automatic save on each message
- **Retrieval**: Load conversation on user login or jurisdiction change
- **Expiration**: No automatic expiration (manual deletion)

#### Context Window
- **LLM context**: 4096 tokens (configurable)
- **Retrieval limit**: Top 15 documents (configurable)
- **Hierarchical context**: Parent chunks provide broader context
- **Message history**: Full conversation history loaded

### Guardrails, Validation, Retries, and Fallback Behavior

#### Jurisdiction Mismatch Detection
- **Keywords**: India-specific and International-specific keyword lists
- **Detection**: Checks query against selected jurisdiction
- **Response**: Suggests jurisdiction switch with explanation
- **Implementation**: `detect_jurisdiction_mismatch()` in `chat_service.py`

#### LLM Fallback
- **Trigger**: Rate limit errors on primary LLM
- **Fallback**: Automatic switch to NVIDIA NIM
- **Detection**: Checks for rate limit indicators in error messages
- **Implementation**: `invoke_with_fallback()` in `llm.py`

#### Citation Validation
- **Format**: Ensures citations follow [Source: Document Name] format
- **Source mapping**: Validates citations against retrieved documents
- **Fallback**: Extracts citations from context if LLM fails
- **Confidence**: High if valid citations, Low otherwise

#### Safe Abstention
- **Out-of-scope detection**: Checks if retrieval returns no results
- **General knowledge mode**: Falls back to general knowledge if no retrieval
- **Disclaimer**: Always includes legal disclaimer
- **Response**: Graceful handling with clear messaging

### Model Evaluation and Limitations

#### Evaluation Script
- **File**: `scripts/evaluate_rag.py`
- **Metrics**: Retrieval accuracy, citation correctness, response quality
- **Status**: Not fully implemented
- **Recommendation**: Implement RAG evaluation framework

#### Known Limitations
- **Neo4j graph**: Empty, no graph retrieval enhancement
- **Knowledge graph**: No automated population pipeline
- **Translation**: Limited to external translation API
- **Conversation history**: No pagination for large conversations
- **Rate limiting**: Global limit, no per-user limits
- **Error recovery**: Limited retry logic for transient failures

---

## 10. API and Component Integration

### Frontend-Backend Communication

#### Authentication Flow
```mermaid
sequenceDiagram
    participant Frontend
    participant Backend
    participant MongoDB

    Frontend->>Backend: POST /api/auth/login (email, password)
    Backend->>MongoDB: Find user by email
    MongoDB-->>Backend: User document
    Backend->>Backend: Verify password hash
    Backend->>Backend: Generate JWT tokens
    Backend-->>Frontend: Token response
    Frontend->>Frontend: Store access_token in localStorage
    Frontend->>Backend: POST /api/chat (Authorization: Bearer token)
    Backend->>Backend: Verify JWT token
    Backend->>Backend: Extract user_id from token
    Backend->>MongoDB: Get user by user_id
    MongoDB-->>Backend: User document
    Backend-->>Frontend: Chat response
```

#### Standard Chat Integration
- **Frontend**: `ChatContext.sendMessage()` → `chatApi.sendMessage()`
- **Backend**: `POST /api/chat` → `ChatService.process_query()` → `AgenticRAG.invoke()`
- **Response**: `ChatResponse` → Frontend display with citations

#### AG-UI Streaming Integration
- **Frontend**: `AgUIChat` component with EventSource
- **Backend**: `POST /api/ag-ui` → LangGraph streaming
- **Events**: `TEXT_MESSAGE_CONTENT` events for streaming tokens
- **Implementation**: `ag_ui.py` with LangGraph streaming support

### Module References

#### Chat Flow
- **Frontend**: `frontend/src/context/ChatContext.jsx` (sendMessage)
- **API**: `frontend/src/services/chatApi.js` (sendMessage)
- **Backend**: `backend/app/api/chat.py` (chat endpoint)
- **Service**: `backend/app/services/chat_service.py` (process_query)
- **Agents**: `backend/app/graph/agents.py` (AgenticRAGWorkflow)

#### Classification Flow
- **Frontend**: `frontend/src/components/Classification/ClassifierFlow.jsx`
- **API**: `frontend/src/services/classifyApi.js`
- **Backend**: `backend/app/api/classify.py` (classify endpoint)
- **Logic**: `ai_classify_formulation()` with RAG-enhanced classification

#### Patent Flow
- **Frontend**: `frontend/src/components/Patent/PatentNoveltyChecker.jsx`
- **Backend**: `backend/app/api/patent.py` (novelty-check endpoint)
- **Agent**: `backend/app/graph/agents.py` (PatentNoveltyAgent)

#### Authentication Flow
- **Frontend**: `frontend/src/context/AuthContext.jsx`
- **Backend**: `backend/app/api/auth.py` (login, register, me)
- **Service**: `backend/app/services/auth_service.py`
- **Utilities**: `backend/app/core/auth.py` (JWT functions)

---

## 11. Setup and Execution

### Prerequisites

#### Backend
- Python 3.10 or higher
- pip package manager
- Qdrant Cloud account (or local Qdrant instance)
- MongoDB Atlas account (or local MongoDB instance)
- API keys:
  - Groq API Key (required)
  - Cohere API Key (required)
  - LlamaParse API Key (required)
  - NVIDIA NIM API Key (optional, for fallback LLM)
  - Neo4j credentials (optional, for knowledge graph)

#### Frontend
- Node.js 18 or higher
- npm or yarn package manager

### Dependency Installation

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

### Environment Variable Configuration

#### Backend (.env)
```env
# Required
LLAMAPARSE_API_KEY=your_llamaparse_api_key
COHERE_API_KEY=your_cohere_api_key
QDRANT_URL=https://your-qdrant-cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
GROQ_API_KEY=your_groq_api_key

# Optional
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ayurpedia
MONGODB_DB_NAME=ayurpedia
NVIDIA_NIM_API_KEY=your_nvidia_api_key
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NEO4J_URI=neo4j+s://your-neo4j-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
SENTRY_DSN=your_sentry_dsn

# Configuration
GROQ_MODEL=llama-3.3-70b-versatile
FALLBACK_MODEL=deepseek-ai/deepseek-v4-flash-0731
EMBEDDING_DIMENSION=1024
BATCH_SIZE=100
PARENT_CHUNK_SIZE=2000
CHILD_CHUNK_SIZE=400
CHUNK_OVERLAP=100
PARENT_OVERLAP=200
TOP_K_RESULTS=15
CONFIDENCE_THRESHOLD=0.7
RATE_LIMIT_PER_MINUTE=60
FRONTEND_URL=http://localhost:5173
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

### Database Setup

#### MongoDB Atlas
1. Create MongoDB Atlas account
2. Create cluster (free tier available)
3. Create database `ayurpedia`
4. Create user with read/write permissions
5. Get connection string
6. Set `MONGODB_URI` in .env

#### Qdrant Cloud
1. Create Qdrant Cloud account
2. Create API key
3. Set `QDRANT_URL` and `QDRANT_API_KEY` in .env
4. Collections are created automatically on first run

#### Neo4j Aura (Optional)
1. Create Neo4j Aura account
2. Create instance
3. Get connection URI, username, password
4. Set `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` in .env
5. Note: System runs without Neo4j if unavailable

### Running the Application

#### Start Backend
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```
Server starts at `http://localhost:8000`

#### Start Frontend
```bash
cd frontend
npm run dev
```
Frontend starts at `http://localhost:5173`

#### Document Ingestion (One-time setup)
```bash
cd backend
source venv/bin/activate
python scripts/run_ingestion.py
```
Optional flags:
- `--recreate`: Delete and recreate Qdrant collections
- `--parent-overlap`: Override parent chunk overlap

### Running Tests and Development Scripts

#### Tests
- No automated test suite currently implemented
- Manual testing via frontend UI
- API testing via Swagger UI at `http://localhost:8000/docs`

#### Development Scripts
- `scripts/run_ingestion.py`: Document ingestion
- `scripts/evaluate_rag.py`: RAG evaluation (not fully implemented)

---

## 12. Configuration and Environment Variables

### Environment Variables Table

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `LLAMAPARSE_API_KEY` | LlamaParse for PDF parsing | Yes | None |
| `COHERE_API_KEY` | Cohere embeddings | Yes | None |
| `QDRANT_URL` | Qdrant cloud URL | Yes | None |
| `QDRANT_API_KEY` | Qdrant API key | Yes | None |
| `GROQ_API_KEY` | Groq LLM API key | Yes | None |
| `MONGODB_URI` | MongoDB connection string | No | In-memory fallback |
| `MONGODB_DB_NAME` | MongoDB database name | No | ayurpedia |
| `NVIDIA_NIM_API_KEY` | NVIDIA NIM API key | No | None |
| `NVIDIA_NIM_BASE_URL` | NVIDIA NIM base URL | No | https://integrate.api.nvidia.com/v1 |
| `NEO4J_URI` | Neo4j connection URI | No | neo4j+s://localhost:7687 |
| `NEO4J_USER` | Neo4j username | No | neo4j |
| `NEO4J_PASSWORD` | Neo4j password | No | password |
| `SENTRY_DSN` | Sentry error tracking | No | None |
| `GROQ_MODEL` | Groq model name | No | llama-3.3-70b-versatile |
| `FALLBACK_MODEL` | Fallback LLM model | No | deepseek-ai/deepseek-v4-flash-0731 |
| `EMBEDDING_DIMENSION` | Embedding vector dimension | No | 1024 |
| `BATCH_SIZE` | Embedding batch size | No | 100 |
| `PARENT_CHUNK_SIZE` | Parent chunk size | No | 2000 |
| `CHILD_CHUNK_SIZE` | Child chunk size | No | 400 |
| `CHUNK_OVERLAP` | Chunk overlap | No | 100 |
| `PARENT_OVERLAP` | Parent chunk overlap | No | 200 |
| `TOP_K_RESULTS` | Retrieval top-k | No | 15 |
| `CONFIDENCE_THRESHOLD` | Response confidence threshold | No | 0.7 |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | No | 60 |
| `FRONTEND_URL` | Frontend URL for CORS | No | http://localhost:5173 |
| `JWT_SECRET_KEY` | JWT signing key | No | your-secret-key-change-in-production |
| `JWT_ALGORITHM` | JWT algorithm | No | HS256 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration | No | 30 |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration | No | 7 |

---

## 13. Testing and Validation

### Existing Tests
- No automated test suite currently implemented
- Manual testing via frontend UI
- API testing via Swagger UI at `http://localhost:8000/docs`

### Test Coverage
- **Backend**: No unit tests, no integration tests
- **Frontend**: No unit tests, no component tests
- **End-to-end**: No E2E tests

### How to Execute Tests
- Manual testing required
- Swagger UI for API testing
- Frontend UI for end-to-end testing

### Important Gaps in Coverage
- **Unit tests**: Missing for all backend services and utilities
- **Integration tests**: Missing for API endpoints
- **Component tests**: Missing for React components
- **E2E tests**: Missing for user flows
- **RAG evaluation**: Partial implementation in `evaluate_rag.py`
- **Load testing**: Not implemented
- **Security testing**: Not implemented

---

## 14. Deployment

### Current Deployment Architecture
- **Development**: Local development with hot reload
- **Backend**: Uvicorn server with auto-reload
- **Frontend**: Vite dev server with HMR
- **Databases**: Cloud services (Qdrant, MongoDB, Neo4j)

### Deployment Configuration
- **Environment**: Development (not production-ready)
- **CORS**: Allows all origins (production needs restrictions)
- **Rate limiting**: Global limit (production needs per-user limits)
- **Error tracking**: Sentry integration (optional)
- **Logging**: INFO level (production needs structured logging)

### Production Deployment (Not Implemented)
- **Backend**: Docker containerization
- **Frontend**: Static build with nginx
- **Databases**: Managed cloud services
- **CI/CD**: Not implemented
- **Monitoring**: Limited to Sentry (optional)
- **Load balancing**: Not implemented

---

## 15. Error Handling, Security, and Reliability

### Input Validation
- **Backend**: Pydantic models for all request/response schemas
- **Frontend**: HTML5 validation and custom validators
- **Sanitization**: Basic input sanitization
- **Length limits**: Query max 1000 characters

### Secret Management
- **Environment variables**: All secrets in .env file
- **Git exclusion**: .env in .gitignore
- **Production**: Secret manager not implemented (recommendation: use AWS Secrets Manager, HashiCorp Vault, or similar)

### API Protection
- **Rate limiting**: SlowAPI global limit (60 requests/minute)
- **CORS**: Configurable origins (currently allows all)
- **JWT authentication**: Required for protected routes
- **HTTPS**: Not enforced (development only)

### Logging
- **Backend**: Python logging with INFO level
- **Request logging**: All requests logged with method and path
- **Error logging**: All exceptions logged with stack traces
- **Structured logging**: Not implemented

### Retries and Failure Recovery
- **LLM fallback**: Automatic switch to NVIDIA NIM on rate limit
- **MongoDB fallback**: In-memory storage if MongoDB unavailable
- **Neo4j fallback**: Graceful degradation to vector-only retrieval
- **Qdrant retry**: No retry logic (recommendation: implement exponential backoff)
- **API retry**: No retry logic (recommendation: implement for transient failures)

---

## 16. Current Limitations

### Technical Limitations
1. **Neo4j Knowledge Graph**: Empty graph, no automated population pipeline
2. **Testing**: No automated test suite
3. **Deployment**: Not production-ready, no containerization
4. **Monitoring**: Limited error tracking, no performance monitoring
5. **Rate Limiting**: Global limit only, no per-user limits
6. **Conversation History**: No pagination for large conversations
7. **Translation**: Limited to external translation API
8. **File Upload**: No support for custom document upload
9. **Graph Visualization**: Disabled due to empty graph
10. **Conversation Sidebar**: Not fully implemented

### Functional Limitations
1. **Knowledge Graph**: No graph-based retrieval enhancement
2. **RAG Evaluation**: Limited evaluation metrics
3. **User Analytics**: No usage analytics or dashboards
4. **Collaboration**: No real-time collaboration features
5. **Mobile**: No mobile app or PWA
6. **Offline**: No offline mode
7. **Voice**: No voice input/output
8. **Export**: Limited JSON export for conversations
9. **Search**: No advanced search in conversation history
10. **Classification**: Limited to 7 categories, no custom categories

### Known Issues
1. **Neo4j Connection**: DNS resolution issues in some environments
2. **Graph Retrieval**: Returns 0 nodes due to empty graph
3. **Verbose Logging**: Excessive startup logs (partially addressed)
4. **Response Format**: Complex format causes parsing errors (addressed with fallback)
5. **Conversation Loading**: 404 errors for some conversation IDs (due to MongoDB fallback)
6. **Conversation Sorting Error**: TypeError when sorting conversations with mixed datetime/string formats (fixed - see Recent Fixes below)

---

## 16.5 Recent Fixes and Updates

### MongoDB Sorting Fix (2026-10-17)
**Issue**: TypeError when listing conversations - comparison between datetime objects and ISO format strings caused sorting to fail
**Error**: `TypeError: '<' not supported between instances of 'datetime.datetime' and 'str'`
**Root Cause**: MongoDB stores timestamps as datetime objects, while in-memory fallback stores as ISO format strings. When sorting conversations by `updated_at`, mixed types caused comparison errors.
**Solution**: Implemented normalization function in `app/core/mongodb.py`:
- Modified `list_conversations()` to normalize `updated_at` fields to strings before sorting
- Modified `list_classifications()` with same fix for `created_at` fields
- Function converts datetime objects to ISO format strings for consistent comparison
**Impact**: Fixed conversation listing and classification listing endpoints, now handles both MongoDB (datetime) and in-memory (string) storage formats

---

## 17. Implementation Status and Roadmap

### Implemented and Verified
- ✅ FastAPI backend with async support
- ✅ React frontend with routing
- ✅ Agentic RAG with LangGraph (QueryUnderstanding, VectorRetriever, Reasoning, Citation agents)
- ✅ Hierarchical chunking with parent-child retrieval
- ✅ Jurisdiction-aware retrieval (India, International, Both)
- ✅ Query expansion with legal terms
- ✅ Relevance boosting for retrieval precision
- ✅ LLM fallback (Groq → NVIDIA NIM)
- ✅ MongoDB persistence with in-memory fallback
- ✅ JWT authentication with access/refresh tokens
- ✅ Formulation classification with AI+RAG
- ✅ Patent novelty checker with Section 3(p) analysis
- ✅ AG-UI streaming endpoint integration
- ✅ Multilingual support (10+ languages via translation API)
- ✅ Citation enforcement with confidence scoring
- ✅ Jurisdiction mismatch detection
- ✅ Human facilitator escalation (UI only)
- ✅ Privacy settings and consent management
- ✅ Rate limiting middleware
- ✅ Document ingestion pipeline with LlamaParse
- ✅ Qdrant vector database with two collections
- ✅ Neo4j integration (graceful degradation)

### Partially Implemented
- ⚠️ Neo4j knowledge graph (connected but empty)
- ⚠️ RAG evaluation (script exists but not fully implemented)
- ⚠️ Conversation sidebar (UI exists but not fully functional)
- ⚠️ Knowledge graph visualization (disabled due to empty graph)
- ⚠️ Sentry error tracking (optional, not always configured)

### Planned or Missing
- ❌ Knowledge graph population pipeline
- ❌ Automated test suite (unit, integration, E2E)
- ❌ Production deployment configuration
- ❌ Docker containerization
- ❌ CI/CD pipeline
- ❌ Advanced analytics dashboard
- ❌ Per-user rate limiting
- ❌ Conversation pagination
- ❌ Custom document upload
- ❌ Advanced search in conversation history
- ❌ Mobile app or PWA
- ❌ Offline mode
- ❌ Voice input/output
- ❌ Real-time collaboration features
- ❌ Integration with AYUSH Ministry databases
- ❌ Patent drafting assistance
- ❌ Automated compliance checking

### Recommended Next Steps
1. **Testing**: Implement automated test suite (pytest for backend, Jest for frontend)
2. **Knowledge Graph**: Build pipeline to populate Neo4j with legal concepts
3. **Deployment**: Create Docker containers and production deployment guide
4. **Monitoring**: Implement structured logging and performance monitoring
5. **Security**: Implement per-user rate limiting and CORS restrictions
6. **Evaluation**: Complete RAG evaluation framework with metrics
7. **Pagination**: Add pagination for conversation history
8. **Search**: Implement advanced search in conversations
9. **Upload**: Add custom document upload feature
10. **Analytics**: Build usage analytics dashboard

---

## 18. Important File Reference

| File Path | Implementation Details |
|-----------|----------------------|
| `backend/main.py` | FastAPI entry point, lifespan management, router inclusion, middleware setup |
| `backend/app/core/config.py` | Environment configuration, validation, and settings management |
| `backend/app/core/llm.py` | LLM client with Groq primary and NVIDIA NIM fallback |
| `backend/app/core/database.py` | Qdrant vector database client with hierarchical chunking support |
| `backend/app/core/mongodb.py` | MongoDB Atlas connection manager with in-memory fallback |
| `backend/app/core/neo4j.py` | Neo4j knowledge graph connection (optional) |
| `backend/app/graph/agents.py` | LangGraph agents (QueryUnderstanding, VectorRetriever, Reasoning, Citation, PatentNovelty) |
| `backend/app/rag/retriever.py` | Jurisdiction-aware retrieval with hierarchical chunking and query expansion |
| `backend/app/rag/hierarchical.py` | Parent-child chunk expansion logic |
| `backend/app/services/chat_service.py` | Chat processing logic with jurisdiction mismatch detection |
| `backend/app/services/auth_service.py` | Authentication logic with user management |
| `backend/app/api/chat.py` | Chat endpoint with JWT authentication |
| `backend/app/api/classify.py` | Formulation classification endpoint with AI+RAG |
| `backend/app/api/patent.py` | Patent novelty checker endpoint |
| `backend/app/api/auth.py` | Authentication endpoints (login, register, me) |
| `backend/app/models/chat.py` | Chat request/response Pydantic models |
| `backend/app/models/document.py` | Document chunk models with hierarchical support |
| `backend/app/models/patent.py` | Patent novelty models with enums |
| `backend/app/models/user.py` | User models with authentication fields |
| `backend/scripts/run_ingestion.py` | Document ingestion pipeline with LlamaParse |
| `frontend/src/App.jsx` | Root React component with context providers |
| `frontend/src/context/ChatContext.jsx` | Chat state management with MongoDB persistence |
| `frontend/src/context/AuthContext.jsx` | Authentication state management |
| `frontend/src/context/AppContext.jsx` | Application settings (language, jurisdiction) |
| `frontend/src/services/chatApi.js` | Chat API client with JWT authentication |
| `frontend/src/components/Chat/ChatInterface.jsx` | Main chat interface with AG-UI toggle |
| `frontend/src/components/Chat/AgUIChat.jsx` | AG-UI streaming chat component |
| `frontend/src/components/Classification/ClassifierFlow.jsx` | Formulation classification wizard |
| `frontend/src/components/Patent/PatentNoveltyChecker.jsx` | Patent novelty checker UI |
| `frontend/src/routes.jsx` | Route configuration with protected routes |

---

## Verification Summary

### Confirmed Details
- ✅ All file paths and filenames exist in the repository
- ✅ API endpoints match backend implementation
- ✅ Model names and dependencies match source code
- ✅ Package scripts and commands match configuration
- ✅ Database schemas match Pydantic models
- ✅ Agent workflow matches LangGraph implementation
- ✅ Frontend components match directory structure

### Areas Not Verified
- ⚠️ Test execution (no automated tests exist)
- ⚠️ Production deployment (not implemented)
- ⚠️ Knowledge graph population (empty graph)
- ⚠️ RAG evaluation metrics (partial implementation)

### Assumptions Made
- Configuration values are defaults from code (not actual .env values)
- API keys are placeholders (not actual credentials)
- Deployment configuration is development-focused (not production)

### Discrepancies Found
- None significant - documentation accurately reflects codebase state

---

**Document Version**: 1.0  
**Last Updated**: 2026-10-17  
**Repository**: AyurPedia  
**Status**: Comprehensive implementation documentation for current codebase state
