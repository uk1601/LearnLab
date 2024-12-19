# LearnLab Airflow Service

## Overview
Apache Airflow service managing data pipelines and scheduled tasks for the LearnLab platform.

## Technical Stack
- **Language**: Python 3.9
- **Framework**: Apache Airflow 2.7.3
- **Database**: PostgreSQL
- **Dependency Management**: Poetry
- **Docker Image**: python:3.9.6-slim

## Project Structure
```
airflow/
├── dags/              # Airflow DAG definitions
│   └── example_dag.py # Example DAG
├── logs/              # Airflow logs
├── plugins/           # Airflow plugins
├── config/           # Airflow configuration
├── .env              # Environment variables
├── .env.example      # Example environment file
├── Dockerfile        # Docker configuration
├── poetry.toml       # Poetry configuration
├── poetry.lock       # Locked dependencies
└── pyproject.toml    # Project dependencies and metadata
```

## Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.9"
apache-airflow = "2.7.3"
apache-airflow-providers-postgres = "^5.7.1"
apache-airflow-providers-http = "^4.6.0"
pandas = "^2.1.3"
requests = "^2.31.0"
python-dotenv = "^1.0.0"
psycopg2-binary = "^2.9.9"
Flask-Session = "^0.5.0"
```

## Docker Configuration
- Uses slim Python image for reduced size
- Poetry for dependency management
- Custom initialization script
- Database health checks
- Runs on port 8080

## Environment Variables
```env
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://postgres:postgres@db:5432/airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True
AIRFLOW__WEBSERVER__SECRET_KEY=your_secret_key_here
```

## Features
Current implemented features:
- Airflow webserver setup
- PostgreSQL integration
- Custom DAG loading
- Health checks
- Database migration handling

## Development
1. Local Setup:
```bash
python -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
```

2. Run Airflow:
```bash
poetry run airflow webserver
```

## Docker Commands
```bash
# Build the service
docker-compose build airflow

# Run the service
docker-compose up airflow

# View logs
docker-compose logs -f airflow
```

## Database Configuration
- Uses shared PostgreSQL database
- Automatic database initialization
- Migration handling
- Connection pooling

## Development Progress
Current implementation includes:
- Basic Airflow setup
- Docker configuration
- Database integration
- Example DAG
- Poetry dependency management
- Health check implementation

Next planned implementations:
- Custom operators
- Production DAGs
- Monitoring setup
- Alert configuration