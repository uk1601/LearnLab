from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from ...core.security import get_current_user
from ...services.notification_service import notification_manager
import logging
from jose import jwt
from ...core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    try:
        # Verify token and get user
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            logger.error(f"Invalid token - no user_id")
            await websocket.close(code=1008)
            return

        logger.info(f"WebSocket connection attempt from user {user_id}")
        
        # Connect websocket
        await notification_manager.connect(user_id, websocket)
        logger.info(f"WebSocket connected for user {user_id}")

        # Keep connection alive
        while True:
            try:
                # Wait for any message (ping/pong will be handled automatically)
                data = await websocket.receive_text()
                logger.debug(f"Received message from {user_id}: {data}")
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user_id}")
                await notification_manager.disconnect(user_id, websocket)
                break
            except Exception as e:
                logger.error(f"Error processing message from {user_id}: {str(e)}")
                break
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.close(code=1011)
        except:
            pass