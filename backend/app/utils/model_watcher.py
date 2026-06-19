"""模型文件监控：检测模型文件变更后自动热加载"""
import asyncio
import os
import time
from typing import Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .logger import logger


class ModelFileHandler(FileSystemEventHandler):
    """监听模型目录的文件变更事件"""

    def __init__(self, reload_callback, debounce_seconds: float = 5.0):
        super().__init__()
        self._reload_callback = reload_callback
        self._debounce_seconds = debounce_seconds
        self._last_event_time: float = 0
        self._pending_reload: Optional[asyncio.Task] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _get_loop(self):
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
        return self._loop

    def on_modified(self, event):
        if event.is_directory:
            return
        # 只关注模型文件（.bin, .safetensors, .json, .txt 等）
        src_path = event.src_path
        if any(
            src_path.endswith(ext)
            for ext in (".bin", ".safetensors", ".json", ".model", ".pth")
        ):
            logger.info(f"Model file changed: {src_path}")
            self._trigger_reload()

    def on_created(self, event):
        if not event.is_directory:
            src_path = event.src_path
            if any(
                src_path.endswith(ext)
                for ext in (".bin", ".safetensors", ".json", ".model", ".pth")
            ):
                logger.info(f"Model file created: {src_path}")
                self._trigger_reload()

    def _trigger_reload(self):
        """防抖处理：短时间内多次变更只触发一次重载"""
        now = time.time()
        if now - self._last_event_time < self._debounce_seconds:
            logger.debug(
                "Debouncing model reload (last event %.1fs ago)",
                now - self._last_event_time,
            )
            return
        self._last_event_time = now

        loop = self._get_loop()
        # 取消之前的待重载任务
        if self._pending_reload and not self._pending_reload.done():
            self._pending_reload.cancel()

        self._pending_reload = loop.create_task(self._do_reload())

    async def _do_reload(self):
        """延迟执行重载，允许文件完全写入"""
        try:
            await asyncio.sleep(self._debounce_seconds)
            self._reload_callback()
        except Exception as e:
            logger.error(f"Auto-reload failed: {e}")


def start_model_watcher(
    watch_path: str,
    reload_callback,
    debounce_seconds: float = 5.0,
) -> Observer:
    """启动模型目录文件监控

    Args:
        watch_path: 要监控的模型目录路径
        reload_callback: 检测到变更后的回调函数
        debounce_seconds: 防抖时间（秒）

    Returns:
        Observer 实例，可通过 observer.stop() 停止监控
    """
    if not os.path.isdir(watch_path):
        logger.warning(
            f"Model watch path does not exist: {watch_path}, "
            f"file watcher not started"
        )
        # 返回一个未启动的 observer
        return Observer()

    logger.info(f"Starting model file watcher on: {watch_path}")
    event_handler = ModelFileHandler(
        reload_callback, debounce_seconds=debounce_seconds
    )
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()
    logger.info("Model file watcher started")
    return observer