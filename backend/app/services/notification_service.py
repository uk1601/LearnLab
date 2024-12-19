from fastapi import WebSocket
from typing import Dict, Set, Optional
from uuid import UUID
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        self._connections: Dict[UUID, Set[WebSocket]] = {}
        self._pending_notifications: Dict[UUID, list] = {}

    async def connect(self, user_id: UUID, websocket: WebSocket):
        """Connect a user's websocket"""
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = set()
        self._connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self._connections[user_id])}")
        
        # Send any pending notifications
        if user_id in self._pending_notifications:
            for message in self._pending_notifications[user_id]:
                await self.send_notification(user_id, message)
            del self._pending_notifications[user_id]

    async def disconnect(self, user_id: UUID, websocket: WebSocket):
        """Disconnect a user's websocket"""
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                del self._connections[user_id]
            logger.info(f"User {user_id} disconnected. Remaining connections: {len(self._connections.get(user_id, set()))}")

    async def send_notification(self, user_id: UUID, message: dict):
        """Send a notification to a specific user"""
        print(f"Attempting to send notification to user {user_id}")
        user_id = str(user_id)
        # If no active connections, store notification for later
        if user_id not in self._connections or not self._connections[user_id]:
            print(f"No active connections. Storing notification for user {user_id}")
            # print all connections available self._connections in the console
            print(self._connections)
            if user_id not in self._pending_notifications:
                self._pending_notifications[user_id] = []
            self._pending_notifications[user_id].append(message)
            logger.info(f"No active connections. Stored notification for user {user_id}")
            return

        disconnected = set()
        success = False
        
        for connection in self._connections[user_id]:
            try:
                await connection.send_json(message)
                logger.info(f"Successfully sent notification to user {user_id}")
                success = True
            except Exception as e:
                logger.error(f"Error sending notification to user {user_id}: {str(e)}")
                disconnected.add(connection)

        # Clean up disconnected sessions
        for connection in disconnected:
            await self.disconnect(user_id, connection)

        # If all attempts failed, store notification for later
        if not success:
            if user_id not in self._pending_notifications:
                self._pending_notifications[user_id] = []
            self._pending_notifications[user_id].append(message)
            logger.info(f"All send attempts failed. Stored notification for user {user_id}")

    async def send_notification_with_retry(self, user_id: UUID, message: dict, max_retries: int = 3):
        """Send a notification with retries"""
        for attempt in range(max_retries):
            if user_id in self._connections and self._connections[user_id]:
                await self.send_notification(user_id, message)
                return
            await asyncio.sleep(1)  # Wait 1 second between retries
        
        # If all retries failed, store the notification
        if user_id not in self._pending_notifications:
            self._pending_notifications[user_id] = []
        self._pending_notifications[user_id].append(message)
        logger.info(f"All retries failed. Stored notification for user {user_id}")

# Global instance
notification_manager = NotificationManager()