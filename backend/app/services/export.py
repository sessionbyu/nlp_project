"""
导出服务

功能：
1. CSV 导出
2. JSON 导出
3. Excel 导出（可选）
"""
import csv
import io
import json
from datetime import datetime
from typing import Optional

from fastapi.responses import StreamingResponse

from ..db.models import PredictionHistory
from ..services.history import query_history


async def export_to_csv(
    session,
    label: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
) -> StreamingResponse:
    """导出预测历史为 CSV"""
    # 查询数据
    result = await query_history(
        session=session,
        page=1,
        page_size=10000,  # 导出全部
        label=label,
        min_score=min_score,
        max_score=max_score,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
    )

    records = result["records"]

    # 创建 CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # 写入表头
    writer.writerow([
        "ID", "输入文本", "预测标签", "置信度", "模型", "IP地址", "创建时间"
    ])

    # 写入数据
    for record in records:
        writer.writerow([
            record.get("id", ""),
            record.get("input_text", ""),
            record.get("label", ""),
            record.get("score", ""),
            record.get("model_key", ""),
            record.get("source_ip", ""),
            record.get("created_at", ""),
        ])

    output.seek(0)

    # 生成文件名
    filename = f"prediction_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


async def export_to_json(
    session,
    label: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
) -> StreamingResponse:
    """导出预测历史为 JSON"""
    # 查询数据
    result = await query_history(
        session=session,
        page=1,
        page_size=10000,
        label=label,
        min_score=min_score,
        max_score=max_score,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
    )

    export_data = {
        "export_time": datetime.now().isoformat(),
        "total": result["total"],
        "filters": {
            "label": label,
            "min_score": min_score,
            "max_score": max_score,
            "keyword": keyword,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        },
        "records": result["records"],
    }

    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)

    filename = f"prediction_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    return StreamingResponse(
        io.BytesIO(json_str.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


async def export_to_excel(
    session,
    label: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
) -> StreamingResponse:
    """导出预测历史为 Excel（需要 pandas + openpyxl）"""
    import pandas as pd
    try:
        # 查询数据
        result = await query_history(
            session=session,
            page=1,
            page_size=10000,
            label=label,
            min_score=min_score,
            max_score=max_score,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
        )

        records = result["records"]

        # 转换为 DataFrame
        df = pd.DataFrame(records)

        # 重命名列
        df = df.rename(columns={
            "id": "ID",
            "input_text": "输入文本",
            "label": "预测标签",
            "score": "置信度",
            "model_key": "模型",
            "source_ip": "IP地址",
            "created_at": "创建时间",
        })

        # 导出到 Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="预测历史", index=False)

        output.seek(0)

        filename = f"prediction_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Excel export requires pandas and openpyxl. Install with: pip install pandas openpyxl",
        )
