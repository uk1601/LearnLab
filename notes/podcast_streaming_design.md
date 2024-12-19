# LearnLab Podcast Streaming System Design

## Project Structure

```
app/
├── services/
│   ├── podcast_service/
│   │   ├── __init__.py           # Exports all service functions
│   │   ├── audio.py              # Audio handling and streaming
│   │   ├── transcript.py         # Transcript processing
│   │   ├── progress.py           # Progress tracking
│   │   ├── analytics.py          # Analytics processing
│   │   └── s3.py                 # S3 operations
│   └── __init__.py
├── models/
│   ├── podcast/
│   │   ├── __init__.py           # Exports all models
│   │   ├── podcast.py            # Podcast model
│   │   ├── progress.py           # Progress tracking model
│   │   └── analytics.py          # Analytics model
│   └── __init__.py
├── schemas/
│   ├── podcast/
│   │   ├── __init__.py           # Exports all schemas
│   │   ├── podcast.py            # Podcast Pydantic schemas
│   │   ├── progress.py           # Progress schemas
│   │   └── analytics.py          # Analytics schemas
│   └── __init__.py
└── api/
    └── v1/
        ├── endpoints/
        │   └── podcast/
        │       ├── __init__.py    # Route exports
        │       ├── podcast.py     # Podcast endpoints
        │       ├── progress.py    # Progress endpoints
        │       └── analytics.py   # Analytics endpoints
        └── __init__.py
```

## Database Models

### 1. Podcast Model (models/podcast/podcast.py)
```python
class Podcast(Base):
    __tablename__ = "podcasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(Text)
    duration = Column(Integer, nullable=False)  # in seconds
    s3_audio_key = Column(String, nullable=False)
    s3_transcript_txt_key = Column(String, nullable=False)
    s3_transcript_vtt_key = Column(String)
    transcript_status = Column(String, default="txt_only")
    total_plays = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
```

### 2. Progress Model (models/podcast/progress.py)
```python
class PodcastProgress(Base):
    __tablename__ = "podcast_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    podcast_id = Column(UUID(as_uuid=True), ForeignKey("podcasts.id", ondelete="CASCADE"))
    current_position = Column(Integer, default=0)
    playback_speed = Column(Float, default=1.0)
    completed_segments = Column(ARRAY(Integer), default=[])
    completion_percentage = Column(Float, default=0.0)
    last_played_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
```

### 3. Analytics Model (models/podcast/analytics.py)
```python
class PodcastAnalytics(Base):
    __tablename__ = "podcast_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    podcast_id = Column(UUID(as_uuid=True), ForeignKey("podcasts.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    total_time_listened = Column(Integer, default=0)
    average_speed = Column(Float, default=1.0)
    number_of_sessions = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
```

## Service Layer Implementation

### 1. Audio Service (services/podcast_service/audio.py)
- Handle audio file uploads to S3
- Generate presigned URLs for streaming
- Validate audio formats and sizes
- Process audio metadata (duration, format)

### 2. Transcript Service (services/podcast_service/transcript.py)
- Process transcript uploads
- Handle text and VTT formats
- Provide transcript synchronization utilities
- Future enhancement: text to VTT conversion

### 3. Progress Service (services/podcast_service/progress.py)
- Track user progress
- Handle segment completion
- Calculate completion percentages
- Manage playback preferences

### 4. Analytics Service (services/podcast_service/analytics.py)
- Track listening sessions
- Calculate user statistics
- Generate learning progress reports
- Handle streak calculations

### 5. S3 Service (services/podcast_service/s3.py)
- Manage S3 operations
- Handle file uploads/downloads
- Generate presigned URLs
- Manage bucket policies and CORS

## API Endpoints

### Podcast Operations
```python
@router.post("/")
async def create_podcast(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    file_id: UUID,
    title: str,
    description: str = None,
    audio_file: UploadFile,
    transcript_file: UploadFile,
) -> PodcastCreate

@router.get("/{podcast_id}")
async def get_podcast(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    podcast_id: UUID,
) -> PodcastDetail
```

### Progress Operations
```python
@router.patch("/{podcast_id}/progress")
async def update_progress(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    podcast_id: UUID,
    progress: PodcastProgressUpdate,
) -> PodcastProgress

@router.get("/{podcast_id}/progress")
async def get_progress(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    podcast_id: UUID,
) -> PodcastProgress
```

### Analytics Operations
```python
@router.get("/analytics/user")
async def get_user_analytics(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserPodcastAnalytics

@router.get("/{podcast_id}/analytics")
async def get_podcast_analytics(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    podcast_id: UUID,
) -> PodcastAnalytics
```

## Frontend Components Structure

```typescript
// components/AudioPlayer/Player.tsx
interface AudioPlayerProps {
  audioUrl: string;
  transcriptUrl: string;
  initialProgress: number;
  onProgressUpdate: (progress: number) => void;
  onSpeedChange: (speed: number) => void;
}

// components/AudioPlayer/TranscriptView.tsx
interface TranscriptViewProps {
  transcriptUrl: string;
  currentTime: number;
  onTimeClick: (time: number) => void;
}

// components/Analytics/ProgressChart.tsx
interface ProgressChartProps {
  analytics: PodcastAnalytics;
  timeframe: 'day' | 'week' | 'month';
}
```

## Implementation Notes

1. Audio Streaming:
   - Use S3 Transfer Acceleration for better upload performance
   - Implement chunk-based streaming for large files
   - Support range requests for seeking

2. Progress Tracking:
   - Update progress every 15 seconds
   - Store completed segments for granular progress
   - Implement smart resume functionality

3. Analytics:
   - Daily aggregation of listening data
   - Calculate learning streaks
   - Store session-based metrics

4. Frontend Considerations:
   - Implement proper error handling for network issues
   - Add offline support capability
   - Handle audio buffering states
