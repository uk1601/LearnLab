import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
import json
import traceback

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # File handler for detailed logging
    file_handler = logging.FileHandler(
        logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}_app.log"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Console handler for basic logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def log_error(logger: logging.Logger, error: Exception, additional_info: dict = None):
    """
    Log an error with full traceback and additional context
    """
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc()
    }
    if additional_info:
        error_info.update(additional_info)
    
    logger.error(json.dumps(error_info, indent=2))

class RequestResponseLoggingMiddleware:
    """
    Middleware to log all requests and responses
    """
    async def __call__(self, request: Any, call_next: Any):
        # Create logger for this request
        logger = setup_logger("request")
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        try:
            body = await request.json()
            logger.debug(f"Request body: {json.dumps(body, indent=2)}")
        except:
            pass

        try:
            response = await call_next(request)
            logger.info(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            log_error(logger, e, {'request_path': str(request.url)})
            raise