import requests
import streamlit as st

API_URL = "http://backend:8000/api/v1/predict"


st.title("NLP预测平台")


text = st.text_input("输入文本")


if st.button("预测"):
    with st.spinner("模型推理中..."):
        response = requests.post(API_URL, json={"text": text})

    result = response.json()

    st.success(result["result"])
