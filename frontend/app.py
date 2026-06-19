# app.py (在 frontend 容器内运行)
import os
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import requests
import streamlit as st

# ==============================
# 后端 API 配置
# ==============================
BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
PREDICT_URL = f"{BACKEND_BASE_URL}/api/v1/predict"
MODELS_URL = f"{BACKEND_BASE_URL}/api/v1/models"
HISTORY_URL = f"{BACKEND_BASE_URL}/api/v1/history"
RECENT_URL = f"{BACKEND_BASE_URL}/api/v1/history/recent"
STATS_URL = f"{BACKEND_BASE_URL}/api/v1/history/stats"

# ==============================
# 页面配置
# ==============================
st.set_page_config(
    page_title="NLP 预测平台",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================
# 侧边栏导航
# ==============================
st.sidebar.title("🧭 导航")
page = st.sidebar.radio("选择页面", ["📝 文本预测", "📊 历史记录", "📈 统计概览"])


# ==============================
# ---- 公共函数 ----
# ==============================
def call_api(url: str, method: str = "GET", json_data: Optional[dict] = None) -> Optional[dict]:
    """通用 API 调用封装"""
    try:
        if method == "GET":
            resp = requests.get(url, timeout=10)
        elif method == "POST":
            resp = requests.post(url, json=json_data, timeout=30)
        else:
            st.error(f"不支持的请求方法: {method}")
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ 无法连接到后端服务 ({BACKEND_BASE_URL})")
    except requests.exceptions.HTTPError as e:
        st.error(f"后端返回 HTTP 错误: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"请求发生错误: {e}")
    return None


# ==============================
# 页面 1: 文本预测
# ==============================
if page == "📝 文本预测":
    st.title("📝 文本情感预测")

    # ---- 获取可用模型列表 ----
    models_info = call_api(MODELS_URL)
    available_models = models_info.get("available_models", ["bert"]) if models_info else ["bert"]
    default_model = models_info.get("default_model", "bert") if models_info else "bert"
    default_index = available_models.index(default_model) if default_model in available_models else 0

    col1, col2 = st.columns([3, 1])
    with col1:
        text = st.text_area("输入要分析的文本", placeholder="请输入中文文本...", height=150)
    with col2:
        st.markdown("### 💡 使用说明")
        st.markdown("""
        - 输入任意中文文本
        - 选择推理模型
        - 点击「开始预测」按钮
        - 查看情感分析结果
        - 结果会自动保存到历史记录
        """)

    # ---- 模型选择器 ----
    model_key = st.selectbox(
        "🤖 选择模型",
        options=available_models,
        index=default_index,
        help="选择用于情感分析的模型（VADER 速度快，BERT 准确度高）",
    )

    if st.button("🚀 开始预测", type="primary", use_container_width=True):
        if not text.strip():
            st.warning("⚠️ 请输入一些文本!")
        else:
            with st.spinner(f"🤖 模型推理中... (使用 {model_key.upper()})"):
                result = call_api(
                    PREDICT_URL,
                    method="POST",
                    json_data={"text": text.strip(), "model_key": model_key},
                )

            if result:
                label = result.get("label", "未知")
                score = result.get("score", 0)

                # 展示结果
                col_a, col_b = st.columns(2)
                with col_a:
                    if "正面" in label or "positive" in label.lower():
                        st.success(f"### 🟢 {label}")
                    else:
                        st.error(f"### 🔴 {label}")
                with col_b:
                    st.metric("置信度", f"{score:.4f}", delta=f"{score * 100:.1f}%")
                    progress_color = (
                        "normal" if score > 0.5 else "normal"
                    )
                    st.progress(min(score, 1.0))


# ==============================
# 页面 2: 历史记录查询
# ==============================
elif page == "📊 历史记录":
    st.title("📊 预测历史记录")

    # ---- 过滤参数 ----
    st.markdown("### 🔍 查询条件")
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            page_num = st.number_input("页码", min_value=1, value=1, step=1)
            page_size = st.select_slider("每页条数", options=[10, 20, 50, 100], value=20)
        with col2:
            label_filter = st.selectbox("标签过滤", options=["全部", "正面", "负面"], index=0)
            keyword = st.text_input("文本关键词搜索", placeholder="输入关键词...")
        with col3:
            min_score = st.slider("最低置信度", min_value=0.0, max_value=1.0, value=0.0, step=0.05)
            max_score = st.slider("最高置信度", min_value=0.0, max_value=1.0, value=1.0, step=0.05)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        use_date_filter = st.checkbox("启用时间范围过滤")
    if use_date_filter:
        with col_d2:
            date_range = st.date_input(
                "选择日期范围",
                value=(datetime.now() - timedelta(days=7), datetime.now()),
                key="date_range",
            )

    # ---- 查询按钮 ----
    if st.button("🔍 查询历史", type="primary", use_container_width=True):
        params = {
            "page": page_num,
            "page_size": page_size,
            "min_score": min_score,
            "max_score": max_score,
        }
        if label_filter != "全部":
            params["label"] = label_filter
        if keyword.strip():
            params["keyword"] = keyword.strip()
        if use_date_filter and len(date_range) == 2:
            params["start_date"] = date_range[0].isoformat()
            params["end_date"] = date_range[1].isoformat()

        # 构建查询字符串
        query_parts = [f"{k}={v}" for k, v in params.items()]
        query_str = "&".join(query_parts)
        full_url = f"{HISTORY_URL}?{query_str}"

        with st.spinner("查询中..."):
            data = call_api(full_url)

        if data:
            records = data.get("records", [])
            total = data.get("total", 0)
            total_pages = data.get("total_pages", 0)

            st.markdown(f"### 📋 查询结果 (共 {total} 条，第 {page_num}/{total_pages} 页)")

            if not records:
                st.info("暂无匹配的历史记录")
            else:
                # 转换为 DataFrame 展示
                df = pd.DataFrame(records)
                # 重命名列
                column_map = {
                    "id": "编号",
                    "input_text": "输入文本",
                    "label": "预测标签",
                    "score": "置信度",
                    "source_ip": "来源 IP",
                    "created_at": "创建时间",
                }
                df_display = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

                # 处理 score 列格式化
                if "置信度" in df_display.columns:
                    df_display["置信度"] = df_display["置信度"].apply(lambda x: f"{x:.4f}")

                # 标签着色
                def color_label(val):
                    if "正面" in str(val):
                        return "background-color: #d4edda; color: #155724"
                    elif "负面" in str(val):
                        return "background-color: #f8d7da; color: #721c24"
                    return ""

                styled_df = df_display.style.map(color_label, subset=["预测标签"] if "预测标签" in df_display.columns else [])

                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True,
                )

                # 最近记录快速查看
                st.markdown("---")
                st.markdown("### ⚡ 最近 10 条记录")
                recent = call_api(RECENT_URL + "?limit=10")
                if recent and recent.get("records"):
                    df_recent = pd.DataFrame(recent["records"])
                    df_recent["score"] = df_recent["score"].apply(lambda x: f"{x:.4f}")
                    column_map_recent = {k: v for k, v in column_map.items() if k in df_recent.columns}
                    df_recent_display = df_recent.rename(columns=column_map_recent)
                    st.dataframe(
                        df_recent_display.style.map(color_label, subset=["预测标签"] if "预测标签" in df_recent_display.columns else []),
                        use_container_width=True,
                        hide_index=True,
                    )


# ==============================
# 页面 3: 统计概览
# ==============================
elif page == "📈 统计概览":
    st.title("📈 预测统计概览")

    if st.button("🔄 刷新统计数据", type="primary", use_container_width=True):
        stats = call_api(STATS_URL)
        if stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总预测次数", stats.get("total_predictions", 0))
            with col2:
                st.metric("平均置信度", f"{stats.get('average_score', 0):.4f}")
            with col3:
                label_dist = stats.get("label_distribution", {})
                total = sum(label_dist.values()) or 1
                st.metric("正面/负面比", f"{label_dist.get('正面', 0)} / {label_dist.get('负面', 0)}")

            # 标签分布图
            st.markdown("### 标签分布")
            if label_dist:
                dist_data = pd.DataFrame(
                    {"标签": list(label_dist.keys()), "数量": list(label_dist.values())}
                )
                st.bar_chart(dist_data.set_index("标签")["数量"])
            else:
                st.info("暂无数据")
    else:
        # 自动加载统计
        auto_stats = call_api(STATS_URL)
        if auto_stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总预测次数", auto_stats.get("total_predictions", 0))
            with col2:
                st.metric("平均置信度", f"{auto_stats.get('average_score', 0):.4f}")
            with col3:
                label_dist = auto_stats.get("label_distribution", {})
                st.metric("正面/负面比", f"{label_dist.get('正面', 0)} / {label_dist.get('负面', 0)}")

            st.markdown("### 标签分布")
            if label_dist:
                dist_data = pd.DataFrame(
                    {"标签": list(label_dist.keys()), "数量": list(label_dist.values())}
                )
                st.bar_chart(dist_data.set_index("标签")["数量"])