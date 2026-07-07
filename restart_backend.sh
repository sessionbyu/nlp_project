#!/bin/bash
echo "=============================================="
echo "重启后端服务（应用限流配置）"
echo "=============================================="

cd /home/user/nlp_project

# 重新构建并启动后端
docker compose up -d backend

# 等待启动
echo ""
echo "⏳ 等待后端启动..."
sleep 5

# 检查状态
if docker compose ps backend | grep -q "Up"; then
    echo "✅ 后端服务已启动"
    
    # 检查健康状态
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 健康检查通过"
    else
        echo "⚠️  健康检查未通过，请稍等片刻"
    fi
else
    echo "❌ 后端服务未正常启动，请检查日志："
    docker compose logs backend
fi

echo ""
echo "=============================================="
echo "完成"
echo "=============================================="
