# Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT UI LAYER                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ Dashboard  │  │  Document  │  │  Employee  │  │    Q&A     │  │
│  │            │  │   Upload   │  │ Management │  │ Assistant  │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                   │
│  │ Onboarding │  │  Progress  │  │  Settings  │                   │
│  │   Plans    │  │  Tracking  │  │            │                   │
│  └────────────┘  └────────────┘  └────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Requests
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    app.py (Streamlit App)                    │  │
│  │  - Route handling                                            │  │
│  │  - UI rendering                                              │  │
│  │  - User interaction                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  agent.py     │    │  ingest.py    │    │ scheduler.py  │
│               │    │               │    │               │
│  AI Agent     │    │  Document     │    │  Reminder     │
│  - Q&A        │    │  Processor    │    │  Scheduler    │
│  - Plan Gen   │    │  - PDF Parse  │    │  - Email      │
│  - Checklist  │    │  - Chunking   │    │  - WhatsApp   │
│               │    │  - Embeddings │    │  - Cron Jobs  │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                     │                     │
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                  │
│                                                                      │
│  ┌──────────────────────┐        ┌──────────────────────┐          │
│  │   db.py              │        │   ChromaDB           │          │
│  │   (SQLite)           │        │   (Vector Store)     │          │
│  │                      │        │                      │          │
│  │  - Employees         │        │  - Document          │          │
│  │  - Plans             │        │    Embeddings        │          │
│  │  - Progress          │        │  - Vector Search     │          │
│  │  - Reminders         │        │  - Metadata         │          │
│  │  - Documents         │        │                      │          │
│  └──────────────────────┘        └──────────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  OpenAI API   │    │  SMTP Server  │    │  Twilio API   │
│               │    │               │    │               │
│  - GPT-3.5    │    │  - Email      │    │  - WhatsApp   │
│  - Embeddings │    │    Delivery   │    │    Messages   │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Data Flow

### Document Ingestion Flow

```
PDF Upload
    │
    ▼
[ingest.py]
    │
    ├─► Extract Text (PyPDF2)
    │
    ├─► Chunk Text (1000 chars, 200 overlap)
    │
    ├─► Generate Embeddings (OpenAI/Default)
    │
    ├─► Store in ChromaDB
    │
    └─► Update Database (metadata)
```

### Q&A Flow

```
User Question
    │
    ▼
[agent.py]
    │
    ├─► Query ChromaDB (vector search)
    │
    ├─► Retrieve Top 5 Results
    │
    ├─► Build Context
    │
    ├─► Call OpenAI API
    │
    ├─► Generate Answer
    │
    └─► Return Answer + Citations
```

### Onboarding Plan Generation Flow

```
Employee Data
    │
    ▼
[agent.py]
    │
    ├─► Query Knowledge Base (role-specific)
    │
    ├─► Query Knowledge Base (general)
    │
    ├─► Build Context
    │
    ├─► Call OpenAI API
    │
    ├─► Parse Plan Structure
    │
    ├─► Extract Checklist Items
    │
    ├─► Save to Database
    │
    └─► Create Progress Tasks
```

### Reminder Flow

```
Scheduled Reminder
    │
    ▼
[scheduler.py]
    │
    ├─► Check Pending Reminders
    │
    ├─► Get Employee Info
    │
    ├─► Format Message
    │
    ├─► Send via Channel
    │   ├─► Email (SMTP)
    │   └─► WhatsApp (Twilio)
    │
    └─► Mark as Sent
```

## Component Details

### 1. Streamlit UI (app.py)
- **Purpose**: User interface for all interactions
- **Pages**: Dashboard, Document Upload, Employee Management, Onboarding Plans, Q&A, Progress Tracking, Settings
- **State Management**: Session state for database connections and agents

### 2. AI Agent (agent.py)
- **Purpose**: Handle AI-powered features
- **Dependencies**: OpenAI API, LangChain, Document Ingester
- **Functions**:
  - Answer questions with citations
  - Generate personalized onboarding plans
  - Create checklists

### 3. Document Ingester (ingest.py)
- **Purpose**: Process PDFs and build knowledge base
- **Dependencies**: PyPDF2, ChromaDB
- **Functions**:
  - Extract text from PDFs
  - Chunk documents
  - Generate embeddings
  - Store in ChromaDB
  - Query knowledge base

### 4. Scheduler (scheduler.py)
- **Purpose**: Send automated reminders
- **Dependencies**: schedule, smtplib, requests (Twilio)
- **Functions**:
  - Schedule reminders
  - Send emails
  - Send WhatsApp messages
  - Process pending reminders

### 5. Database (db.py)
- **Purpose**: Manage application data
- **Technology**: SQLite
- **Tables**: employees, onboarding_plans, progress, reminders, documents

### 6. ChromaDB
- **Purpose**: Vector storage for document embeddings
- **Technology**: ChromaDB (persistent client)
- **Collection**: onboarding_docs
- **Embeddings**: Default sentence-transformers

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **AI/ML**: OpenAI GPT-3.5, LangChain
- **Vector DB**: ChromaDB
- **Database**: SQLite
- **PDF Processing**: PyPDF2
- **Scheduling**: schedule library
- **Email**: smtplib
- **WhatsApp**: Twilio API

## Security Considerations

1. **API Keys**: Stored in environment variables
2. **Database**: Local SQLite (consider encryption for production)
3. **File Uploads**: Validated file types and sizes
4. **Email/WhatsApp**: Credentials stored securely

## Scalability Considerations

1. **Database**: Can migrate to PostgreSQL/MySQL for production
2. **Vector DB**: ChromaDB can scale with persistent storage
3. **Caching**: Consider adding Redis for frequently accessed data
4. **Load Balancing**: Multiple Streamlit instances behind a load balancer
5. **Async Processing**: Consider Celery for background tasks

## Deployment Options

1. **Local**: Run `streamlit run app.py`
2. **Docker**: Containerize the application
3. **Cloud**: Deploy to Streamlit Cloud, AWS, GCP, Azure
4. **Server**: Deploy on Linux server with systemd service

