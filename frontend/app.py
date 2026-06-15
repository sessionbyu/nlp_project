# app.py (在 frontend 容器内运行)
import os

import requests
import streamlit as st

# 从环境变量读取后端基础 URL
BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")  # 默认值以防万一
API_URL = f"{BACKEND_BASE_URL}/api/v1/predict"  # 构造完整的 API 端点 URL

st.title("NLP预测平台")

text = st.text_input("输入文本")

if st.button("预测"):
    if not text.strip():
        st.warning("请输入一些文本!")
        # continue

    with st.spinner("模型推理中..."):
        try:
            # 这个请求是从 frontend 容器内部发往 backend 容器的
            # 因为 BACKEND_BASE_URL 是 http://backend:8000，所以请求会正确路由
            response = requests.post(API_URL, json={"text": text})
            response.raise_for_status()  # 检查 HTTP 错误

            result = response.json()
            st.success(result.get("label", "预测失败"))
            st.write(f"置信度: {result['score']:.4f}")

        except requests.exceptions.ConnectionError as e:
            # 这里的错误信息会显示在 Streamlit UI 上
            st.error(f"无法连接到后端服务 ({API_URL}): {e}")
        except requests.exceptions.HTTPError as e:
            st.error(f"后端返回HTTP错误: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"请求发生错误: {e}")
        except KeyError:
            st.error(f"后端响应格式异常: {response.text}")
        except Exception as e:
            st.error(f"未知错误: {e}")
