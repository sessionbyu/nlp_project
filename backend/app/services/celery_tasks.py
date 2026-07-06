"""
Celery 异步任务服务

功能：
1. 批量预测任务
2. 文件分析任务
3. 任务状态跟踪
4. 任务结果存储
"""
import os
from typing import Optional, Dict, Any, List
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from ..core.config import settings
from ..utils.logger import logger

# Celery 配置
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

# 创建 Celery 应用
celery_app = Celery(
    "nlp_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟超时
    task_soft_time_limit=29 * 60,  # 软超时
)


# ========== 异步任务定义 ==========

@celery_app.task(bind=True, name="batch_predict_task")
def batch_predict_task(self, texts: List[str], model_key: str = "bert") -> Dict[str, Any]:
    """
    批量预测任务

    Args:
        texts: 文本列表
        model_key: 模型key

    Returns:
        包含任务ID和结果的字典
    """
    task_id = self.request.id
    logger.info(f"Batch predict task started: {task_id}, texts_count={len(texts)}")

    try:
        # 更新任务状态
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": len(texts), "status": "Processing..."}
        )

        # 导入服务（延迟导入避免循环依赖）
        from ..services.inference import predict_text

        # 使用 asyncio 运行异步函数
        results = []
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for i, text in enumerate(texts):
            try:
                result = loop.run_until_complete(predict_text(text, model_key=model_key))
                results.append({
                    "text": text,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Failed to predict text {i}: {e}")
                results.append({
                    "text": text,
                    "success": False,
                    "error": str(e)
                })

            # 更新进度
            if (i + 1) % 10 == 0 or i == len(texts) - 1:
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i + 1,
                        "total": len(texts),
                        "status": f"Processed {i + 1}/{len(texts)}"
                    }
                )

        loop.close()

        logger.info(f"Batch predict task completed: {task_id}")

        return {
            "task_id": task_id,
            "status": "completed",
            "total": len(texts),
            "success": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }

    except Exception as e:
        logger.error(f"Batch predict task failed: {task_id}, error: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task(bind=True, name="analyze_file_task")
def analyze_file_task(
    self,
    file_path: str,
    model_key: str = "bert",
    text_column: Optional[str] = None,
) -> Dict[str, Any]:
    """
    文件分析任务

    Args:
        file_path: 文件路径
        model_key: 模型key
        text_column: 文本列名

    Returns:
        分析结果
    """
    task_id = self.request.id
    logger.info(f"File analysis task started: {task_id}, file={file_path}")

    try:
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 0, "status": "Reading file..."}
        )

        # 读取文件
        import pandas as pd

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(file_path)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path, engine="openpyxl")
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        # 检测文本列
        if not text_column:
            candidates = ["text", "content", "message", "review", "comment"]
            for col in df.columns:
                if any(c in col.lower() for c in candidates):
                    text_column = col
                    break
            if not text_column:
                text_column = df.columns[0]

        texts = df[text_column].dropna().astype(str).tolist()
        total = len(texts)

        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": total, "status": "Analyzing..."}
        )

        # 批量预测
        from ..services.inference import predict_text
        import asyncio

        results = []
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for i, text in enumerate(texts):
            try:
                result = loop.run_until_complete(predict_text(text, model_key=model_key))
                results.append({
                    "text": text,
                    "label": result["label"],
                    "score": result["score"]
                })
            except Exception as e:
                logger.error(f"Failed to analyze text {i}: {e}")
                results.append({
                    "text": text,
                    "error": str(e)
                })

            # 更新进度
            if (i + 1) % 10 == 0 or i == total - 1:
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i + 1,
                        "total": total,
                        "status": f"Processed {i + 1}/{total}"
                    }
                )

        loop.close()

        # 保存结果到文件
        result_df = pd.DataFrame(results)
        result_path = f"{file_path}_results.csv"
        result_df.to_csv(result_path, index=False)

        logger.info(f"File analysis task completed: {task_id}")

        return {
            "task_id": task_id,
            "status": "completed",
            "file_path": file_path,
            "result_path": result_path,
            "total": total,
            "success": sum(1 for r in results if "error" not in r),
            "failed": sum(1 for r in results if "error" in r),
        }

    except Exception as e:
        logger.error(f"File analysis task failed: {task_id}, error: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


# ========== 任务管理服务 ==========

class CeleryTaskService:
    """Celery 任务管理服务"""

    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        result = celery_app.AsyncResult(task_id)

        response = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
        }

        if result.state == "PROGRESS":
            response["progress"] = result.info

        if result.failed():
            response["error"] = str(result.result)

        return response

    @staticmethod
    def revoke_task(task_id: str, terminate: bool = False) -> bool:
        """撤销任务"""
        try:
            celery_app.control.revoke(task_id, terminate=terminate)
            logger.info(f"Task revoked: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke task: {task_id}, error: {e}")
            return False

    @staticmethod
    def get_active_tasks() -> List[Dict[str, Any]]:
        """获取活跃任务列表"""
        inspect = celery_app.control.inspect()
        active = inspect.active()
        if not active:
            return []

        tasks = []
        for worker, worker_tasks in active.items():
            for task in worker_tasks:
                tasks.append({
                    "task_id": task["id"],
                    "name": task["name"],
                    "worker": worker,
                    "time_start": task.get("time_start"),
                    "args": task.get("args", []),
                })

        return tasks


# 全局任务服务实例
celery_task_service = CeleryTaskService()
