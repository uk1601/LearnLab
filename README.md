# LearnLab 🧠🔍

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0+-00a393.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-13.0+-black.svg)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10.8+-blue.svg)](https://www.docker.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.48-purple.svg)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation](https://img.shields.io/badge/docs-Codelabs-blue.svg)](https://codelabs-preview.appspot.com/?file_id=1kMzJ_qRJrDknPFatF1raPvsoJUatl_-tfJuICo7p4EM#0)

> **Transforming static documents into dynamic, multi-modal learning experiences through advanced RAG, semantic chunking, and intelligent agent orchestration.**

## 🌟 Quick Links

- [GitHub Issues and Tasks](https://github.com/orgs/DAMG7245-Big-Data-Sys-SEC-02-Fall24/projects/7/views/1)
- [Codelabs Documentation](https://codelabs-preview.appspot.com/?file_id=1kMzJ_qRJrDknPFatF1raPvsoJUatl_-tfJuICo7p4EM#0)
- [Project Submission Video](https://drive.google.com/drive/u/0/folders/1wgYeUY-HsDuWcqGq1hSNVRQ3gvQBMLZC)

## 📋 Project Overview

LearnLab transforms traditional educational content into engaging, interactive learning experiences. Through advanced AI-powered document intelligence, we convert static PDFs into multiple synchronized learning formats:

- 🎧 **Immersive Podcasts** - Audio learning with dynamically generated conversational scripts
- 📝 **Smart Flashcards** - Spaced repetition learning with context-aware explanations  
- 📊 **Adaptive Quizzes** - Multi-difficulty assessments with intelligent feedback
- 📘 **Interactive Blogs** - Structured explanations with enhanced comprehension support
- 🐦 **Shareable Tweets** - Concise knowledge summaries for social learning

The system employs cutting-edge techniques like semantic chunking with dynamically adjusted thresholds, OpenAI embeddings, and window-based context preservation to ensure high-quality information retrieval and generation across all learning formats.

## 🚀 Key Technical Features

### 📱 Advanced RAG Architecture
- **Semantic Chunking Engine** - Adaptive token segmentation (100-500) with 92% retrieval accuracy
- **Dynamic Thresholding** - Context-aware document splitting with window size 2 for coherence
- **Vector Database Integration** - Pinecone vector storage with optimized embeddings for sub-second retrieval

### 🧩 Multi-Agent Orchestration
- **LangGraph Agent System** - Five specialized content transformation agents with distributed workflows
- **State Management** - Context-preserving transitions between generation phases
- **Semantic Caching** - Upstash vector caching with 97% similarity threshold, reducing API costs by 41%

### 🔄 Real-Time Infrastructure
- **WebSocket Stream Processing** - Live progress updates with bi-directional communication
- **JWT Authentication** - Secure token-based identity management with granular permissions
- **Cloud-Native Deployment** - GCP + AWS hybrid infrastructure with automatic failover

### 📊 Learning Analytics
- **Progress Tracking** - Cross-format learning metrics with personalized insights
- **Comprehension Analysis** - Performance evaluation across content types
- **Engagement Metrics** - Detailed usage statistics for educational optimization

## 🛠️ Technology Stack

### Backend Engineering
- ![Python](https://img.shields.io/badge/Python-FFD43B?style=flat&logo=python&logoColor=blue)
- ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
- ![LangChain](https://img.shields.io/badge/LangChain-121D33?style=flat)
- ![LangGraph](https://img.shields.io/badge/LangGraph-6309DE?style=flat)
- ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
- ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)

### Frontend Engineering
- ![Next.js](https://img.shields.io/badge/Next.js-black?style=flat&logo=next.js&logoColor=white)
- ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)
- ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
- ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)

### AI/ML Infrastructure
- ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)
- ![Pinecone](https://img.shields.io/badge/Pinecone-40C5F4?style=flat)
- ![Upstash](https://img.shields.io/badge/Upstash-00E9A3?style=flat)
- ![Elevenlabs](https://img.shields.io/badge/ElevenLabs-232F3E?style=flat)

### Cloud & DevOps
- ![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat&logo=google-cloud&logoColor=white)
- ![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat&logo=amazon-aws&logoColor=white)
- ![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat&logo=docker&logoColor=white)
- ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=github-actions&logoColor=white)
- ![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-017CEE?style=flat&logo=Apache%20Airflow&logoColor=white)

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph frontend["Frontend Layer"]
        NextJS["Next.js UI"]
        StreamlitUi["Streamlit Analytics"]
        WebsocketClient["WebSocket Client"]
    end

    subgraph backend["Backend Services"]
        FastAPI["FastAPI Server"]
        WebsocketServer["WebSocket Server"]
        AuthService["JWT Authentication"]
        
        subgraph contentEngine["Content Engine"]
            RAGService["RAG Service"]
            PodcastAgent["Podcast Generator"]
            FlashcardAgent["Flashcard Generator"]
            QuizAgent["Quiz Generator"]
            BlogAgent["Blog Generator"]
            TweetAgent["Tweet Generator"]
        end
        
        subgraph storage["Data Layer"]
            PostgreSQL["PostgreSQL"]
            S3["AWS S3"]
            PineconeDB["Pinecone Vector DB"]
            UpstashCache["Upstash Semantic Cache"]
        end
        
        subgraph orchestration["Workflow Orchestration"]
            LangGraph["LangGraph"]
            Airflow["Apache Airflow"]
        end
    end

    subgraph externalServices["External Services"]
        OpenAI["OpenAI API"]
        ElevenLabs["ElevenLabs TTS"]
    end

    %% Connections
    NextJS <--> FastAPI
    StreamlitUi <--> FastAPI
    WebsocketClient <--> WebsocketServer
    FastAPI <--> AuthService
    FastAPI <--> contentEngine
    contentEngine <--> orchestration
    contentEngine <--> storage
    contentEngine <--> externalServices
    RAGService <--> PineconeDB
    PodcastAgent <--> S3
    contentEngine <--> UpstashCache
    AuthService <--> PostgreSQL
```

## 📱 User Flow

```mermaid
flowchart TD
  A[Start] --> B[Login Screen]
  B --> C{Authentication}
  C -->|Success| D[Dashboard]
  C -->|Failure| B
  
  D --> E{New or Existing Resource}
  
  E -->|Upload New| F[Upload PDF Resource]
  F --> G[Processing Document]
  G --> H{Select Learning Mode}
  
  E -->|Pick Existing| H
  
  H -->|Option 1| I[Podcast Generation]
  I --> I1[Generate Audio]
  I1 --> I2[Listen & Learn]
  I2 --> M[Learning Metrics]
  
  H -->|Option 2| J[Flashcard Mode]
  J --> J1[View Cards]
  J1 --> J2[Practice Cards]
  J2 --> M
  
  H -->|Option 3| K[Quiz Mode]
  K --> K1[Take Quiz]
  K1 --> K2[Review Answers]
  K2 --> M
  
  H -->|Option 4| N1[Blog Generation]
  N1 --> N2[Read Blog]
  N2 --> M
  
  H -->|Option 5| T1[Tweet Generation]
  T1 --> T2[Share Tweet]
  T2 --> M
  
  M --> N{Continue Learning?}
  N -->|Yes| H
  N -->|No| O{Share Progress?}
  
  O -->|Yes| P[Generate Content]
  P --> P1[Blog Post]
  P --> P2[Social Media Post]
  O -->|No| Q[Exit]
  P1 --> Q
  P2 --> Q
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker
- GCP Account
- AWS Account

### Setup Environment
```bash
# Clone repository
git clone <repository-url>
cd LearnLab

# Initialize environments and configurations
./setup-env.sh
```

### Start Services
```bash
# Start all services
docker-compose up -d

# Or start specific services
docker-compose up -d frontend backend
```

## 📚 Service Ports

| Service   | Port  | URL                     |
|-----------|-------|----------------------------|
| Frontend  | 3000  | http://localhost:3000   |
| Backend   | 8000  | http://localhost:8000   |
| Streamlit | 8501  | http://localhost:8501   |
| Airflow   | 8080  | http://localhost:8080   |
| Database  | 5432  | postgres://localhost:5432|

## ⚙️ Essential Commands

### Development
```bash
# Build specific service
docker-compose build <service-name>

# View logs
docker-compose logs -f <service-name>

# Restart service
docker-compose restart <service-name>
```

### Database
```bash
# Access PostgreSQL CLI
docker-compose exec db psql -U postgres

# Backup database
docker-compose exec db pg_dump -U postgres learnlab > backup.sql
```

### Cleanup
```bash
# Stop all services
docker-compose down

# Remove volumes
docker-compose down -v
```

## 📂 Project Structure
```
LearnLab/
├── frontend/          # Next.js frontend with TypeScript
├── backend/           # FastAPI backend with LangGraph agents
│   ├── agents/        # Multi-agent orchestration system
│   ├── app/           # Core application logic
│   └── utils/         # Shared utilities and helpers
├── streamlit-ui/      # Streamlit analytics dashboard
├── airflow/           # Airflow DAGs for document processing
├── docker/            # Docker configurations
└── docker-compose.yml # Service orchestration
```

## 👨‍💻 Team

- Sai Surya Madhav Rebbapragada
- Uday Kiran Dasari
- Venkat Akash Varun Pemmaraju

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 References

- [OpenNotebookLM](https://github.com/gabrielchua/open-notebooklm)
- [Bark](https://github.com/suno-ai/bark)
- [Llama Recipes](https://github.com/meta-llama/llama-recipes)
- [EduChain](https://github.com/satvik314/educhain)
- [Consillium App](https://www.consillium.app/)
- [Median](https://github.com/5uru/Median)
