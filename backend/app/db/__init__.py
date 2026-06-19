"""数据库模块"""
from app.db.models import PredictionHistory
from app.db.session import async_session, Base, engine, get_async_session

__all__ = ["Base", "engine", "async_session", "get_async_session", "PredictionHistory"]
