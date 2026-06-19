FROM python:3.11-slim

# 安装构建依赖，特别是对 asyncpg 可能有用
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# 升级 pip 并安装依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 下载 NLTK 数据
RUN python -c "import nltk; nltk.download('vader_lexicon', quiet=True)"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
