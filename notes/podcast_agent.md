# podcast_agent :V1

A sophisticated RAG (Retrieval-Augmented Generation) based podcast generation system that creates AI-powered podcasts from PDF documents using LangGraph, OpenAI, and ElevenLabs.


1. **PDFProcessor**: Handles document processing and vector storage
2. **RAGApplication**: Manages document querying and context retrieval
3. **PodcastGenerator**: Orchestrates the podcast generation workflow
4. **S3Storage**: Manages podcast file storage in AWS S3
5. **SemanticCache**: Handles caching using Upstash vector database

## 🌟 Features

- PDF document processing and indexing using Pinecone vector database
- Advanced semantic embedding using OpenAI's text-embedding-3-small model
- Dynamic text splitting with RollingWindowSplitter for optimal context preservation
- Context-aware podcast content generation using RAG architecture
- Natural conversational script generation with two distinct speakers
- Text-to-speech synthesis using ElevenLabs voices



## 🧠 Semantic Embeddings

### Why Semantic Embeddings?

Our system leverages OpenAI's text-embedding-3-small model for several key advantages:

1. **Semantic Understanding**:
   - Captures meaning beyond simple keyword matching
   - Understands context, synonyms, and related concepts
   - Handles technical terminology and domain-specific language effectively

2. **Dynamic Text Splitting**:
   ```python
   splitter = RollingWindowSplitter(
       encoder=self.encoder,
       dynamic_threshold=True,
       min_split_tokens=100,
       max_split_tokens=500,
       window_size=2,
       plot_splits=True
   )
   ```
   - Maintains semantic coherence in document chunks
   - Prevents context fragmentation
   - Adapts split sizes based on content complexity

3. **Improved Retrieval**:
   - Higher accuracy in finding relevant content
   - Better handling of paraphrased concepts
   - Reduced false positives in context retrieval

4. **Context Window Management**:
   - Overlapping windows for continuous context
   - Optimal chunk sizing for GPT model input
   - Metadata linking for context reconstruction

### Implementation Benefits

1. **Accuracy**:
   - More precise content retrieval compared to traditional keyword search
   - Better understanding of complex technical concepts
   - Improved handling of industry-specific terminology

2. **Performance**:
   - Fast query processing with vector operations
   - Efficient storage and retrieval using Pinecone
   - Scalable to large document collections

3. **Content Quality**:
   - More coherent podcast scripts
   - Better topic selection and expansion
   - Improved context preservation in final output

## Podcast Generation Speedup Docs: 

# Groq Integration for Podcast Generation

## Overview
This integration replaces OpenAI's GPT-4 with Groq's LLama-70B model to significantly improve podcast generation speed, reducing generation time from 3 minutes to approximately 1.5-2 minutes.

## Key Improvements

### Speed Enhancement
- Original GPT-4 pipeline: ~3 minutes
- Groq-powered pipeline: ~1.5-2 minutes
- Nearly 50% reduction in total generation time

### Technical Implementation
```python
from langchain_groq import ChatGroq

self.llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    groq_api_key=GROQ_API_KEY
)
```

### Performance Benefits
1. **Faster Token Processing**: Groq's architecture processes tokens more efficiently
2. **Reduced Latency**: Lower response times for each generation stage
3. **Maintained Quality**: Similar output quality to GPT-4
4. **Cost Efficiency**: Potentially lower API costs compared to GPT-4

## Implementation Requirements
- Groq API key in environment variables
- Updated LangChain dependency to include Groq integration
- No changes needed to existing prompt templates

## Pipeline Optimization
- Topic Expansion: ~30-40 seconds (previously 1 minute)
- Script Generation: ~40-50 seconds (previously 1.5 minutes)
- Script Refinement: ~20-30 seconds (previously 30 seconds)



## 🛠️ Architecture

The system consists of four main components:

1. **PDFProcessor**: Handles document processing and vector storage
2. **RAGApplication**: Manages document querying and context retrieval
3. **PodcastGenerator**: Orchestrates the podcast generation workflow


### Component Details

#### PDFProcessor Class
```python
PDFProcessor(openai_api_key: str, pinecone_api_key: str)
```
Core methods:
- `create_index()`: Initializes Pinecone vector database
- `read_pdf()`: Extracts text content from PDF files
- `index_document()`: Processes and stores document embeddings
- `query()`: Retrieves relevant document chunks
- `get_available_pdfs()`: Lists indexed documents

#### RAGApplication Class
```python
RAGApplication()
```
Core methods:
- `process_document()`: Handles PDF processing workflow
- `query_document()`: Retrieves context using RAG
- `set_current_pdf()`: Sets active document context
- `generate_answer()`: Creates responses using LangChain

#### PodcastGenerator Class
```python
PodcastGenerator()
```
Core methods:
- `generate_podcast()`: Main podcast generation pipeline
- `create_graph()`: Builds the LangGraph workflow
- `synthesize_speech()`: Handles TTS generation
- `expand_topic()`, `generate_script()`, `refine_script()`: Content generation stages

#### S3Storage Class
```python
S3Storage(bucket_name: str)
```
Core methods:
- `upload_file()`: Uploads podcast to S3 with organized structure
- `list_podcasts()`: Retrieves available podcasts
- `sanitize_filename()`: Ensures S3-compatible filenames

Features:
- Organized folder structure: `podcast/{pdf_title}/{podcast_title}_{timestamp}.mp3`
- Automatic file cleanup after upload
- PDF-based podcast filtering
- Error handling for AWS operations

#### PodcastCache Class
```python
PodcastCache()
```
Core methods:
- `get_cached_podcast()`: Retrieves cached podcast based on similar queries
- `cache_podcast()`: Stores podcast data with metadata
- `clear_cache()`: Removes all cached entries
- `generate_cache_key()`: Creates unique keys for query-document pairs

Features:
- Semantic similarity matching (85% threshold)
- Automatic timestamp tracking
- JSON serialization for data storage
- Error handling for cache operations





## Set up environment variables:
```bash
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID_1=voice_id_for_speaker_1
ELEVENLABS_VOICE_ID_2=voice_id_for_speaker_2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_BUCKET_NAME=your_bucket_name
GROQ_API_KEY=your_groq_api_key
UPSTASH_VECTOR_REST_URL=your_upstash_url
UPSTASH_VECTOR_REST_TOKEN=your_upstash_token
```

Available commands:
1. List available documents
2. Index new document
3. Generate podcast from existing document
4. Exit

## 🔄 Workflow

The podcast generation follows this pipeline:
1. Check semantic cache for similar queries
2. Return cached podcast if found (includes S3 URL)
3. If no cache hit:
   - Document indexing and RAG context retrieval
   - Topic expansion and outline creation
   - Script generation with two speakers
   - Script refinement and language enhancement
   - Text-to-speech synthesis
   - S3 storage with organized structure
   - Cache the generated podcast data

## 📊 Visualization

![Podcast Agent v1](/assets/podcast_agent_v2.png)

## ⚠️ Changes to add still 

- Tweak the prompt 

## 🙏 Acknowledgments

- LangChain for the RAG framework
- OpenAI for language models
- ElevenLabs for text-to-speech
- Pinecone for vector storage
- Upstash for Semantic Cacheing
  