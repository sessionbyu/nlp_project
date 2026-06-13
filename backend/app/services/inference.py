import asyncio
import time


def nlp_model(text: str):
    """
    模拟CPU密集型NLP模型
    """

    time.sleep(5)

    return {"result": f"NLP分析:{text}", "length": len(text)}


async def predict_async(text: str):
    result = await asyncio.to_thread(nlp_model, text)

    return result
