# Integrated Content Generation System V2

A sophisticated RAG-based content generation system that creates AI-powered podcasts, quizzes, and flashcards from PDF documents using LangGraph, LangChain, and various AI services.

## 🌟 Core Components

1. **RAGApplication**: Manages document querying and context retrieval
2. **PodcastGenerator**: Orchestrates podcast generation workflow
3. **QuizGenerator**: Creates interactive educational quizzes
4. **ContentEngine**: Produces educational flashcards
5. **S3Storage**: Manages file storage in AWS S3
6. **SemanticCache**: Handles caching using Upstash vector database

## 🚀 Features

### Content Generation
- Multiple content types:
  - Conversational podcasts with TTS
  - Interactive educational quizzes
  - Study-oriented flashcards
- Context-aware content using RAG architecture
- Natural conversational script generation
- Text-to-speech synthesis using ElevenLabs

### Data Processing
- PDF document processing and indexing
- Advanced semantic embedding using LangChain
- Dynamic text splitting for optimal context
- Efficient caching system for repeated queries

### Interactive Features
- Interactive quiz taking functionality
- Detailed quiz feedback and scoring
- Flashcard review system
- Command-line interface for all operations

## 🛠️ Architecture

### Main Components

#### 1. QuizGenerator Class
```python
QuizGenerator(api_key: str, model: str = "learnlm-1.5-pro-experimental")
```
Core methods:
- `generate_quiz()`: Creates quiz from context
- `grade_quiz()`: Evaluates user responses
- `format_quiz_for_display()`: Prepares quiz UI

#### 2. ContentEngine Class
```python
ContentEngine(llm_config: Optional[LLMConfig] = None)
```
Core methods:
- `generate_flashcards()`: Creates study cards
- `display_flashcards()`: Formats for viewing
- `_initialize_llm()`: Sets up language model

#### 3. PodcastGenerator Class
```python
PodcastGenerator()
```
Core methods:
- `generate_content()`: Main content pipeline
- `create_graph()`: Builds workflow
- `generate_tts()`: Handles audio synthesis
- `check_cache()`: Manages content caching

### Data Models

#### Quiz Structure
```python
class QuizSet(BaseModel):
    title: str
    description: str
    questions: List[QuizQuestion]
    total_points: int
    recommended_time: int
```

#### Flashcard Structure
```python
class FlashcardSet(BaseModel):
    title: str
    flashcards: List[Flashcard]
```

## 🔄 Workflow

![Podcast Agent v1](/assets/learnlab_agent.png)


The system follows these pipelines:

### Podcast Generation:
1. Check semantic cache
2. RAG context retrieval
3. Topic expansion
4. Script generation
5. TTS synthesis
6. S3 storage
7. Cache results

### Quiz Generation:
1. Context retrieval
2. Question generation
3. Answer/explanation creation
4. Interactive quiz delivery
5. Scoring and feedback

### Flashcard Creation:
1. Context analysis
2. Key concept extraction
3. Card generation
4. Additional explanations
5. Organized presentation

## ⚙️ Setup

Environment variables needed:
```bash
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID_1=voice_id_for_speaker_1
ELEVENLABS_VOICE_ID_2=voice_id_for_speaker_2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_BUCKET_NAME=your_bucket_name
UPSTASH_VECTOR_REST_URL=your_upstash_url
UPSTASH_VECTOR_REST_TOKEN=your_upstash_token
```

## 📋 Available Commands

1. List available documents
2. Index new document
3. Generate content:
   - Podcast
   - Quiz
   - Flashcards
4. Exit

## 🎯 Use Cases

1. **Educational Content**:
   - Create study materials
   - Generate practice quizzes
   - Produce educational podcasts

2. **Content Repurposing**:
   - Convert documents to audio
   - Create interactive learning materials
   - Generate study aids

3. **Knowledge Testing**:
   - Quiz generation and grading
   - Progress tracking
   - Detailed feedback

## 🙏 Acknowledgments

- LangChain for the framework
- OpenAI and Google for language models
- ElevenLabs for text-to-speech
- Upstash for semantic caching