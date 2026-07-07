"""
WebSocket API 路由

功能：
1. 实时任务进度推送
2. 通知订阅
"""
import uuid
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_async_session
from ...services.auth import get_current_user_ws
from ...services.websocket import manager
from ...utils.logger import logger

router = APIRouter()


@router.websocket("/ws/{task_id}")
async def websocket_task_progress(
    websocket: WebSocket,
    task_id: str,
    token: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_async_session),
):
    """
    WebSocket 端点：订阅任务进度

    客户端连接后，服务器将实时推送任务执行进度

    连接 URL: ws://localhost:8000/api/v1/ws/{task_id}?token={access_token}
    """
    # 验证用户（可选）
    current_user = None
    if token:
        try:
            from ...services.auth import get_current_user
            # WebSocket 不能直接使用 Depends，需要手动验证
            current_user = await get_current_user_ws(token, session)
        except Exception as e:
            logger.warning(f"WebSocket auth failed: {e}")

    connection_id = str(uuid.uuid4())
    user_id = str(current_user.id) if current_user else None

    try:
        await manager.connect(websocket, connection_id, user_id)

        # 发送连接成功消息
        await manager.send_personal_message(
            {
                "type": "connected",
                "connection_id": connection_id,
                "task_id": task_id,
            },
            connection_id,
        )

        # 保持连接并处理客户端消息
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # 处理客户端消息
                if message.get("action") == "ping":
                    await manager.send_personal_message(
                        {"type": "pong", "timestamp": message.get("timestamp")},
                        connection_id,
                    )

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {connection_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await manager.send_personal_message(
                    {"type": "error", "message": str(e)},
                    connection_id,
                )

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        manager.disconnect(connection_id, user_id)
