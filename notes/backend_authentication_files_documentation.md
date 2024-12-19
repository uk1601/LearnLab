# LearnLab Backend Documentation - Authentication & File Management

## Overview
This documentation covers the implementation of user authentication and file management features in the LearnLab backend service.

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE
);
```

### User Sessions Table
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    device_info VARCHAR(255),
    UNIQUE(user_id, refresh_token)
);
```

### Files Table
```sql
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(512) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(127),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false
);
```

## API Endpoints

### Authentication Endpoints

#### 1. Register User
- **Endpoint**: POST /auth/register
- **Description**: Register a new user
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "password": "password",
    "full_name": "John Doe"
  }
  ```

#### 2. Login
- **Endpoint**: POST /auth/login
- **Description**: Login and get access/refresh tokens
- **Request Body**:
  ```json
  {
    "username": "user@example.com",
    "password": "password"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "jwt_token",
    "refresh_token": "refresh_token",
    "token_type": "bearer"
  }
  ```

#### 3. Refresh Token
- **Endpoint**: POST /auth/refresh-token
- **Description**: Get new access token using refresh token
- **Request Body**:
  ```json
  {
    "refresh_token": "refresh_token"
  }
  ```

#### 4. Logout
- **Endpoint**: POST /auth/logout
- **Description**: Invalidate refresh tokens
- **Authentication**: Required (Bearer token)

### File Management Endpoints

#### 1. Upload File
- **Endpoint**: POST /api/upload
- **Description**: Upload file to S3
- **Authentication**: Required
- **Request**: Multipart form data with file
- **Response**: File metadata with download URL

#### 2. List Files
- **Endpoint**: GET /api/files
- **Description**: List all user's files
- **Authentication**: Required
- **Query Parameters**:
  - skip: Number of records to skip
  - limit: Number of records to return

#### 3. Get File
- **Endpoint**: GET /api/files/{file_id}
- **Description**: Get specific file details and download URL
- **Authentication**: Required

#### 4. Delete File
- **Endpoint**: DELETE /api/files/{file_id}
- **Description**: Delete file (soft delete)
- **Authentication**: Required

## AWS S3 Configuration

### Required IAM Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::learnlab-files",
                "arn:aws:s3:::learnlab-files/*"
            ]
        }
    ]
}
```

### Bucket Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement1",
            "Principal": "*",
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "arn:aws:s3:::learnlab-files",
                "arn:aws:s3:::learnlab-files/*"
            ]
        }
    ]
}
```

## Environment Variables
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
```

## Logging System

### Logger Setup
- Created centralized logging configuration
- Logs are stored in the `logs` directory
- Log format includes:
  - Timestamp
  - Log level
  - File name and line number
  - Message
  - Additional context

### Log Categories
1. **Info Logs**
   - Application startup
   - Successful operations
   - User actions

2. **Debug Logs**
   - Detailed operation steps
   - Request/Response data
   - Performance metrics

3. **Error Logs**
   - Exception details
   - Stack traces
   - Error context
   - User context

## Error Handling
- Structured error responses
- Transaction management with rollbacks
- S3 operation cleanup on failures
- User-friendly error messages
- Detailed error logging
- Security error handling

## Architecture Considerations

### Security
- Password hashing using bcrypt
- JWT-based authentication
- Token refresh mechanism
- Secure file access with presigned URLs
- Request validation

### Performance
- Paginated file listings
- Soft delete for files
- Efficient database indexing
- File upload optimization

### Scalability
- Modular code structure
- Separation of concerns
- Environment-based configuration
- Docker containerization

## Testing Instructions

### Local Testing
1. Start the services:
   ```bash
   docker-compose up -d
   ```

2. Test database connection:
   ```bash
   psql -h localhost -U postgres -d learnlab
   ```

3. Verify S3 connection:
   ```python
   import boto3
   s3 = boto3.client('s3')
   s3.list_objects_v2(Bucket='learnlab-files')
   ```

### API Testing
Use tools like Postman or curl to test endpoints:

1. Register User:
```bash
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{
  "email": "test@example.com",
  "username": "testuser",
  "password": "password123",
  "full_name": "Test User"
}'
```

2. Login:
```bash
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{
  "username": "test@example.com",
  "password": "password123"
}'
```

3. Upload File:
```bash
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/file.pdf"
```
