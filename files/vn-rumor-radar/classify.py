# -*- coding: utf-8 -*-
"""
classify.py — Gán nhãn cho mỗi tin:
  sentiment : positive | negative | neutral
  verify    : verified | unverified | debunked

Hai chế độ:
  1. Heuristic từ khoá (mặc định, miễn phí, chạy offline)
  2. Claude API (nếu đặt biến môi trường ANTHROPIC_API_KEY và
     config.USE_CLAUDE_CLASSIFIER = True) — chính xác hơn đáng kể.
"""
import json
import os

import requests

import config

POSITIVE_KW = [
    "tăng trưởng", "lãi kỷ lục", "lợi nhuận tăng", "trúng thầu", "mở rộng",
    "cổ tức", "ký kết", "ký hợp đồng", "hợp đồng mới", "hợp tác",
    "khởi sắc", "bứt phá", "mua ròng", "tăng vốn", "đối tác mới",
    "đối tác chiến lược", "thưởng cổ phiếu",
]
NEGATIVE_KW = [
    "khởi tố", "bắt", "thanh tra", "vi phạm", "xử phạt", "thua lỗ", "lỗ",
    "bán tháo", "giảm sàn", "nợ xấu", "chậm trả", "huỷ niêm yết",
    "đình chỉ", "cảnh báo", "kiện", "rút vốn", "bán ròng", "lao dốc",
]
DEBUNK_KW = ["bác bỏ", "đính chính", "phủ nhận", "tin giả", "không đúng sự thật"]


def _heuristic(item):
    text = (item["title"] + " " + item["snippet"]).lower()
    neg = sum(kw in text for kw in NEGATIVE_KW)
    pos = sum(kw in text for kw in POSITIVE_KW)
    sentiment = "negative" if neg > pos else "positive" if pos > neg else "neutral"

    if any(kw in text for kw in DEBUNK_KW):
        verify = "debunked"
    elif item["is_rumor_flagged"] or item["source_type"] in ("forum", "social"):
        verify = "unverified"
    else:
        verify = "verified"  # tin báo chính thống, không có dấu hiệu tin đồn

    heat = min(100, 30 + neg * 15 + pos * 10
               + (25 if item["is_rumor_flagged"] else 0)
               + (15 if item["source_type"] != "press" else 0))
    return sentiment, verify, heat


def _claude_batch(items):
    """Phân loại 1 lô tin bằng Claude API. Trả về dict id -> nhãn, lỗi -> None."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    payload_items = [
        {"id": it["id"], "title": it["title"], "snippet": it["snippet"],
         "source_type": it["source_type"]}
        for it in items
    ]
    prompt = (
        "Phân loại các tin sau về công ty niêm yết Việt Nam. Trả về DUY NHẤT "
        "một mảng JSON, mỗi phần tử: {\"id\":..., \"sentiment\":\"positive|"
        "negative|neutral\", \"verify\":\"verified|unverified|debunked\", "
        "\"heat\":1-100}. Quy tắc: verify=verified chỉ khi là tin chính thống "
        "có nguồn rõ ràng; tin đồn/diễn đàn/MXH chưa xác nhận -> unverified; "
        "tin đã bị doanh nghiệp/cơ quan chức năng bác bỏ -> debunked. "
        "heat = mức độ đáng chú ý/lan truyền.\n\n"
        + json.dumps(payload_items, ensure_ascii=False)
    )
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": config.CLAUDE_MODEL,
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        resp.raise_for_status()
        text = "".join(b.get("text", "") for b in resp.json()["content"]
                       if b.get("type") == "text")
        text = text.replace("```json", "").replace("```", "").strip()
        start, end = text.find("["), text.rfind("]")
        parsed = json.loads(text[start:end + 1])
        return {p["id"]: p for p in parsed if "id" in p}
    except Exception as exc:
        print(f"  [Claude classifier lỗi, dùng heuristic] {exc}")
        return None


def classify(items):
    """Gán nhãn cho các item CHƯA có nhãn (in-place)."""
    pending = [it for it in items if "sentiment" not in it]
    if not pending:
        return items

    labels = None
    if config.USE_CLAUDE_CLASSIFIER:
        # chia lô 25 tin/lượt để gọn context
        labels = {}
        for i in range(0, len(pending), 25):
            batch = _claude_batch(pending[i:i + 25])
            if batch is None:
                labels = None
                break
            labels.update(batch)

    for it in pending:
        if labels and it["id"] in labels:
            lab = labels[it["id"]]
            it["sentiment"] = lab.get("sentiment", "neutral")
            it["verify"] = lab.get("verify", "unverified")
            it["heat"] = int(lab.get("heat", 50))
        else:
            it["sentiment"], it["verify"], it["heat"] = _heuristic(it)
    mode = "Claude API" if labels else "heuristic từ khoá"
    print(f"Đã phân loại {len(pending)} tin mới ({mode})")
    return items
