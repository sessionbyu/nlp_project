"""
WebSocket 服务

功能：
1. 实时进度推送
2. 任务状态通知
3. 连接管理
"""
import json
from typing import Any, Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from ..utils.logger import logger


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 活跃连接：{connection_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # 用户订阅：{user_id: Set[connection_id]}
        self.user_subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, connection_id: str, user_id: Optional[str] = None):
        """建立连接"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket

        if user_id:
            if user_id not in self.user_subscriptions:
                self.user_subscriptions[user_id] = set()
            self.user_subscriptions[user_id].add(connection_id)

        logger.info(f"WebSocket connected: {connection_id}, user={user_id}")

    def disconnect(self, connection_id: str, user_id: Optional[str] = None):
        """断开连接"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        if user_id and user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(connection_id)
            if not self.user_subscriptions[user_id]:
                del self.user_subscriptions[user_id]

        logger.info(f"WebSocket disconnected: {connection_id}")

    async def send_personal_message(self, message: Dict[str, Any], connection_id: str):
        """发送个人消息"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")

    async def send_to_user(self, message: Dict[str, Any], user_id: str):
        """发送消息给指定用户的所有连接"""
        if user_id in self.user_subscriptions:
            for connection_id in self.user_subscriptions[user_id]:
                await self.send_personal_message(message, connection_id)

    async def broadcast(self, message: Dict[str, Any]):
        """广播消息给所有连接"""
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {connection_id}: {e}")
                disconnected.append(connection_id)

        # 清理断开的连接
        for connection_id in disconnected:
            self.disconnect(connection_id)

    async def send_progress(
        self,
        connection_id: str,
        task_id: str,
        current: int,
        total: int,
        status: str,
        result: Optional[Dict[str, Any]] = None,
    ):
        """发送进度更新"""
        message = {
            "type": "progress",
            "task_id": task_id,
            "current": current,
            "total": total,
            "progress_percent": round(current / total * 100, 2) if total > 0 else 0,
            "status": status,
        }
        if result:
            message["result"] = result

        await self.send_personal_message(message, connection_id)

    async def send_notification(
        self,
        connection_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ):
        """发送通知"""
        msg = {
            "type": "notification",
            "notification_type": notification_type,
            "title": title,
            "message": message,
        }
        if data:
            msg["data"] = data

        await self.send_personal_message(msg, connection_id)


# 全局连接管理器实例
manager = ConnectionManager()
