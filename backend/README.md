# LearnLab Backend Service

## Overview
FastAPI-based backend service handling the core business logic and API endpoints for the LearnLab platform. Features include user authentication, file management with S3 integration, and comprehensive logging.

## Technical Stack
- **Language**: Python 3.12
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Storage**: AWS S3
- **Authentication**: JWT with refresh tokens
- **Dependency Management**: Poetry
- **Docker Image**: python:3.12-slim

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── core/               # Core functionality
│   │   ├── config.py       # Configuration settings
│   │   ├── security.py     # Authentication logic
│   │   ├── database.py     # Database connection
│   │   └── logger.py       # Logging configuration
│   ├── api/
│   │   └── v1/            # API version 1
│   │       ├── auth.py    # Authentication endpoints
│   │       └── files.py   # File management endpoints
│   ├── models/            # SQLAlchemy models
│   │   ├── user.py
│   │   ├── file.py
│   │   └── user_session.py
│   ├── schemas/           # Pydantic schemas
│   │   ├── user.py
│   │   └── file.py
│   └── services/          # Business logic
│       └── s3.py         # S3 integration
├── logs/                  # Application logs
├── .env                   # Environment variables
├── .env.example           # Example environment file
├── Dockerfile             # Docker configuration
├── poetry.toml           # Poetry configuration
├── poetry.lock           # Locked dependencies
└── pyproject.toml        # Project dependencies and metadata
```

## Features
- User Authentication
  - Registration
  - Login/Logout
  - JWT with refresh tokens
  - Session management
- File Management
  - S3 integration
  - File upload/download
  - Presigned URLs
  - Soft delete support
- Comprehensive Logging
  - Request/Response logging
  - Error tracking
  - Performance monitoring
- Security
  - Password hashing
  - Token-based authentication
  - S3 access control

## Dependencies
Key dependencies added:
```toml
[tool.poetry.dependencies]
python = ">=3.12,<3.13"
fastapi = "^0.110.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.9"
boto3 = "^1.34.69"
pydantic-settings = "^2.2.1"
```

## Environment Variables
Required environment variables:
```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/learnlab

# JWT Configuration
JWT_SECRET_KEY=your-256-bit-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_BUCKET_NAME=learnlab-files
AWS_REGION=us-east-1

# Server Configuration
DEBUG=True
ENVIRONMENT=development
```

## API Endpoints

### Authentication
- POST /auth/register - Register new user
- POST /auth/login - User login
- POST /auth/refresh-token - Refresh access token
- POST /auth/logout - User logout

### File Management
- POST /api/upload - Upload file
- GET /api/files - List user's files
- GET /api/files/{file_id} - Get file details
- DELETE /api/files/{file_id} - Delete file

## Development Setup

1. Local Setup:
```bash
python -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
```

2. Environment Configuration:
- Copy .env.example to .env
- Update with your credentials

3. AWS S3 Setup:
- Create S3 bucket
- Configure IAM user with S3 access
- Update bucket policy

4. Run Development Server:
```bash
poetry run uvicorn app.main:app --reload
```

## Docker Commands
```bash
# Build and run all services
docker-compose up -d

# Build specific service
docker-compose build backend

# View logs
docker-compose logs -f backend

# Access PostgreSQL
docker exec -it learnlab-db-1 psql -U postgres -d learnlab
```

## Database
- PostgreSQL 15 with UUID support
- Automatic table creation on startup
- Indexed for performance
- Soft delete functionality
- See database documentation for schema details

## Logging
- Structured logging with context
- Separate files for different log levels
- Performance metrics
- Error tracking with stack traces
- Request/Response logging

## AWS S3 Integration
- Secure file storage
- Presigned URLs for downloads
- User-specific directories
- Automatic cleanup

## Security Considerations
- Password hashing with bcrypt
- JWT token management
- S3 bucket policies
- Request validation
- Error handling

## Testing
```bash
# Run tests
poetry run pytest

# Test coverage
poetry run pytest --cov=app
```

## Documentation
Additional documentation available in the `/notes` directory:
- Complete API documentation
- Database schema details
- Authentication flow
- File management details

## Current Status
Implemented:
- User authentication system
- File management with S3
- Comprehensive logging
- Error handling
- Database schema
- Security measures

Next planned implementations:
- File sharing functionality
- Multi-factor authentication
- Rate limiting
- API documentation with Swagger UI
- Integration tests