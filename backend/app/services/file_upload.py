"""
文件上传服务

功能：
1. CSV/Excel 文件解析
2. 批量文本提取
3. 文件验证与安全检查
4. 支持大文件上传
"""
import io
import os
import uuid
from typing import Any, List, Optional, Dict

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..utils.logger import logger


class FileUploadService:
    """文件上传与处理服务"""

    # 允许的文件类型
    ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".txt", ".json"}
    # 最大文件大小 (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    # 最大文本数量
    MAX_TEXTS = 10000

    def __init__(self):
        self.upload_dir = os.getenv("UPLOAD_DIR", "/tmp/uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    async def validate_file(self, file: UploadFile) -> None:
        """验证文件合法性"""
        # 检查文件扩展名
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {ext}. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        # 检查文件大小
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到开头

        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file_size / 1024 / 1024:.1f}MB. Max: {self.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
            )

    async def extract_texts_from_file(
        self,
        file: UploadFile,
        text_column: Optional[str] = None,
    ) -> List[str]:
        """
        从文件中提取文本列表

        Args:
            file: 上传的文件
            text_column: 文本列名（CSV/Excel），如果为None则尝试自动检测

        Returns:
            文本列表
        """
        ext = os.path.splitext(file.filename)[1].lower()
        content = await file.read()
        await file.seek(0)

        try:
            if ext in [".csv"]:
                return await self._extract_from_csv(io.BytesIO(content), text_column)
            elif ext in [".xlsx", ".xls"]:
                return await self._extract_from_excel(io.BytesIO(content), text_column)
            elif ext == ".txt":
                return await self._extract_from_txt(content)
            elif ext == ".json":
                return await self._extract_from_json(content)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {ext}")
        except Exception as e:
            logger.error(f"Failed to extract texts from file: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    async def _extract_from_csv(self, file_obj: io.BytesIO, text_column: Optional[str]) -> List[str]:
        """从CSV提取文本"""
        import pandas as pd

        df = pd.read_csv(file_obj)

        # 自动检测文本列
        if not text_column:
            text_column = self._detect_text_column(df)

        if text_column not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Column '{text_column}' not found. Available: {', '.join(df.columns)}"
            )

        texts = df[text_column].dropna().astype(str).tolist()

        if len(texts) > self.MAX_TEXTS:
            raise HTTPException(
                status_code=400,
                detail=f"Too many texts: {len(texts)}. Max: {self.MAX_TEXTS}"
            )

        return texts

    async def _extract_from_excel(self, file_obj: io.BytesIO, text_column: Optional[str]) -> List[str]:
        """从Excel提取文本"""
        import pandas as pd

        df = pd.read_excel(file_obj, engine="openpyxl")

        # 自动检测文本列
        if not text_column:
            text_column = self._detect_text_column(df)

        if text_column not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Column '{text_column}' not found. Available: {', '.join(df.columns)}"
            )

        texts = df[text_column].dropna().astype(str).tolist()

        if len(texts) > self.MAX_TEXTS:
            raise HTTPException(
                status_code=400,
                detail=f"Too many texts: {len(texts)}. Max: {self.MAX_TEXTS}"
            )

        return texts

    async def _extract_from_txt(self, content: bytes) -> List[str]:
        """从纯文本提取（按行分割）"""
        text = content.decode("utf-8")
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        if len(lines) > self.MAX_TEXTS:
            raise HTTPException(
                status_code=400,
                detail=f"Too many lines: {len(lines)}. Max: {self.MAX_TEXTS}"
            )

        return lines

    async def _extract_from_json(self, content: bytes, text_column: Optional[str] = None) -> List[str]:
        """从JSON提取文本"""
        import pandas as pd

        data = pd.read_json(io.BytesIO(content))

        # 尝试找到文本列
        if not text_column:
            text_column = self._detect_text_column(data)

        if text_column not in data.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Column '{text_column}' not found. Available: {', '.join(data.columns)}"
            )

        texts = data[text_column].dropna().astype(str).tolist()
        return texts

    def _detect_text_column(self, df: Any) -> str:
        """自动检测文本列"""
        # 优先查找包含 'text', 'content', 'message' 的列
        candidates = ["text", "content", "message", "review", "comment", "body"]
        for col in df.columns:
            if any(candidate in col.lower() for candidate in candidates):
                return col

        # 返回第一个对象类型的列
        for col in df.columns:
            if df[col].dtype == object:
                return col

        # 默认返回第一列
        return df.columns[0]

    async def save_uploaded_file(self, file: UploadFile) -> str:
        """
        保存上传的文件到磁盘

        Returns:
            保存的文件路径
        """
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1]
        filename = f"{file_id}{ext}"
        file_path = os.path.join(self.upload_dir, filename)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"File saved: {filename}")
        return file_path


# 全局文件上传服务实例
file_upload_service = FileUploadService()
