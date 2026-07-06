#!/bin/bash

# 个人设置页面快速修复脚本
# 方案1: 使用开发模式（推荐）

echo "========================================="
echo "  个人设置页面修复脚本"
echo "========================================="
echo ""

cd /home/user/nlp_project

echo "步骤1: 停止当前前端容器"
echo "-----------------------------------------"
docker compose stop frontend-vue
echo "✓ 已停止"
echo ""

echo "步骤2: 检查node_modules"
echo "-----------------------------------------"
if [ ! -d "frontend-vue/node_modules" ]; then
    echo "⚠️  依赖未安装，正在安装..."
    cd frontend-vue
    npm install
    cd ..
    echo "✓ 依赖安装完成"
else
    echo "✓ 依赖已安装"
fi
echo ""

echo "步骤3: 启动开发服务器"
echo "-----------------------------------------"
echo "提示: 开发服务器将在后台运行"
echo "访问地址: http://localhost:5173"
echo ""
echo "启动命令:"
echo "  cd frontend-vue"
echo "  npm run dev"
echo ""
echo "或者手动启动:"
echo "  cd /home/user/nlp_project/frontend-vue"
echo "  npm run dev"
echo ""

echo "========================================="
echo "  完成"
echo "========================================="
echo ""
echo "下一步:"
echo "1. cd /home/user/nlp_project/frontend-vue"
echo "2. npm run dev"
echo "3. 访问 http://localhost:5173"
echo "4. F12 → Console → 清除缓存:"
echo "   localStorage.clear(); sessionStorage.clear(); location.reload()"
echo "5. 重新登录测试"
echo ""
