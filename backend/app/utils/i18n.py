"""
国际化 (i18n) 支持

功能：
1. 多语言消息
2. 语言检测
3. 翻译字典
"""
from typing import Dict, Optional


class I18n:
    """国际化服务"""

    def __init__(self, default_language: str = "en"):
        self.default_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {
            "en": {
                # 通用
                "success": "Success",
                "error": "Error",
                "not_found": "Not found",
                "unauthorized": "Unauthorized",
                "forbidden": "Forbidden",
                "bad_request": "Bad request",
                # 用户相关
                "user_created": "User created successfully",
                "user_not_found": "User not found",
                "invalid_credentials": "Invalid username or password",
                "account_disabled": "Account is disabled",
                # 预测相关
                "prediction_success": "Prediction completed",
                "prediction_failed": "Prediction failed",
                "invalid_text": "Text cannot be empty",
                "model_not_found": "Model not available",
                # 文件相关
                "file_uploaded": "File uploaded successfully",
                "file_too_large": "File is too large",
                "unsupported_format": "Unsupported file format",
                # 任务相关
                "task_queued": "Task queued successfully",
                "task_in_progress": "Task in progress",
                "task_completed": "Task completed",
                "task_failed": "Task failed",
            },
            "zh": {
                # 通用
                "success": "成功",
                "error": "错误",
                "not_found": "未找到",
                "unauthorized": "未授权",
                "forbidden": "禁止访问",
                "bad_request": "请求错误",
                # 用户相关
                "user_created": "用户创建成功",
                "user_not_found": "用户未找到",
                "invalid_credentials": "用户名或密码错误",
                "account_disabled": "账户已禁用",
                # 预测相关
                "prediction_success": "预测完成",
                "prediction_failed": "预测失败",
                "invalid_text": "文本不能为空",
                "model_not_found": "模型不可用",
                # 文件相关
                "file_uploaded": "文件上传成功",
                "file_too_large": "文件过大",
                "unsupported_format": "不支持的文件格式",
                # 任务相关
                "task_queued": "任务已排队",
                "task_in_progress": "任务进行中",
                "task_completed": "任务完成",
                "task_failed": "任务失败",
            },
        }

    def t(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        翻译文本

        Args:
            key: 翻译键
            language: 语言代码（en/zh）
            **kwargs: 格式化参数

        Returns:
            翻译后的文本
        """
        lang = language or self.default_language

        # 获取翻译
        translation = self.translations.get(lang, {}).get(key)

        if translation is None:
            #  fallback to default language
            translation = self.translations.get(self.default_language, {}).get(key, key)

        # 格式化
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError:
                pass

        return translation

    def get_supported_languages(self) -> list:
        """获取支持的语言列表"""
        return list(self.translations.keys())


# 全局 i18n 实例
i18n = I18n(default_language="en")


def detect_language(text: str) -> str:
    """
    检测文本语言

    Args:
        text: 输入文本

    Returns:
        语言代码 (en/zh)
    """
    # 简单的中文检测
    chinese_chars = len([c for c in text if '一' <= c <= '鿿'])
    total_chars = len(text.strip())

    if total_chars == 0:
        return "en"

    chinese_ratio = chinese_chars / total_chars
    return "zh" if chinese_ratio > 0.3 else "en"


def get_language_from_header(accept_language: Optional[str] = None) -> str:
    """
    从 Accept-Language 头部获取语言

    Args:
        accept_language: Accept-Language 头部值

    Returns:
        语言代码
    """
    if not accept_language:
        return "en"

    # 解析 Accept-Language
    languages = accept_language.split(",")
    for lang in languages:
        lang = lang.strip().split(";")[0].lower()
        if lang in ["zh", "zh-cn", "zh-hans"]:
            return "zh"
        elif lang in ["en", "en-us", "en-gb"]:
            return "en"

    return "en"
