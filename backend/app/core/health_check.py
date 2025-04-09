# app/core/health_check.py
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .database import engine

logger = logging.getLogger(__name__)

def check_database_connection():
    """Check if the database is accessible and return status."""
    try:
        # Try to execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("✅ Database connection successful")
        return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

def perform_health_checks():
    """Run all health checks at startup."""
    logger.info("🔍 Performing system health checks...")
    
    # Database check
    db_status = check_database_connection()
    
    # Add more checks as needed (Redis, external APIs, etc.)
    
    if db_status:
        logger.info("✅ All system checks passed!")
    else:
        logger.warning("⚠️ Some system checks failed. See logs for details.")
        
    return {
        "database": db_status,
        # Add other services as needed
    }