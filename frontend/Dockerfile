FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# 创建一个启动脚本
RUN echo '#!/bin/bash\n\
mkdir -p /app/logs\n\
streamlit run app.py --server.address=0.0.0.0 --server.port=8501 \
>> /app/logs/streamlit.log 2>&1' > /entrypoint.sh && chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
