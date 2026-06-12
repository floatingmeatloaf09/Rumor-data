# -*- coding: utf-8 -*-
"""
crawler.py — Quét các nguồn RSS, nhận diện mã cổ phiếu, khử trùng lặp.
Mỗi tin lưu kèm LINK GỐC để truy cập trực tiếp.
"""
import hashlib
import html
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone

import feedparser
import requests

import config

VN_TZ = timezone(timedelta(hours=7))
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "items.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; VNRumorRadar/1.0)"}


def _clean(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _item_id(link: str, title: str) -> str:
    return hashlib.sha1((link or title).encode("utf-8")).hexdigest()[:16]


def _match_tickers(text: str):
    """Trả về danh sách mã CK xuất hiện trong đoạn text."""
    found = set()
    upper = " " + text.upper() + " "
    lower = text.lower()
    for ticker, aliases in config.TICKERS.items():
        # Mã viết hoa đứng độc lập (tránh khớp nhầm trong từ khác)
        if re.search(r"(?<![A-Z0-9])" + re.escape(ticker) + r"(?![A-Z0-9])", upper):
            found.add(ticker)
            continue
        for alias in aliases:
            if alias.lower() in lower:
                found.add(ticker)
                break
    return sorted(found)


def _has_rumor_keyword(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in config.RUMOR_KEYWORDS)


def _parse_time(entry) -> str:
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                dt = datetime.fromtimestamp(time.mktime(t), tz=timezone.utc)
                return dt.astimezone(VN_TZ).isoformat()
            except Exception:
                pass
    return datetime.now(VN_TZ).isoformat()


def _all_feeds():
    feeds = list(config.FEEDS)
    if config.ENABLE_GOOGLE_NEWS_PER_TICKER:
        for ticker in config.TICKERS:
            feeds.append({
                "name": f"Google News · {ticker}",
                "url": config.GOOGLE_NEWS_TEMPLATE.format(ticker=ticker),
                "source_type": "press",
            })
    return feeds


def fetch_feed(feed_cfg):
    """Tải 1 feed, trả về danh sách item thô. Lỗi mạng -> bỏ qua, không crash."""
    items = []
    try:
        resp = requests.get(feed_cfg["url"], headers=HEADERS,
                            timeout=config.REQUEST_TIMEOUT)
        parsed = feedparser.parse(resp.content)
    except Exception as exc:
        print(f"  [bỏ qua] {feed_cfg['name']}: {exc}")
        return items

    for entry in parsed.entries[: config.MAX_ITEMS_PER_FEED]:
        title = _clean(getattr(entry, "title", ""))
        summary = _clean(getattr(entry, "summary", ""))[:400]
        link = getattr(entry, "link", "") or ""
        if not title or not link:
            continue
        text = f"{title}. {summary}"
        tickers = _match_tickers(text)
        if not tickers:
            continue  # chỉ giữ bài có nhắc tới mã đang theo dõi
        items.append({
            "id": _item_id(link, title),
            "tickers": tickers,
            "title": title,
            "snippet": summary,
            "link": link,
            "source_name": feed_cfg["name"],
            "source_type": feed_cfg["source_type"],
            "published": _parse_time(entry),
            "is_rumor_flagged": _has_rumor_keyword(text),
        })
    print(f"  [ok] {feed_cfg['name']}: {len(items)} bài khớp mã theo dõi")
    return items


def load_existing():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save(items):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)


def crawl():
    """Quét toàn bộ nguồn, gộp với dữ liệu cũ, cắt bỏ tin quá hạn."""
    existing = load_existing()
    known_ids = {it["id"] for it in existing}

    new_items = []
    for feed_cfg in _all_feeds():
        for it in fetch_feed(feed_cfg):
            if it["id"] not in known_ids:
                known_ids.add(it["id"])
                new_items.append(it)

    cutoff = (datetime.now(VN_TZ) - timedelta(days=config.KEEP_DAYS)).isoformat()
    merged = [it for it in existing + new_items if it["published"] >= cutoff]
    merged.sort(key=lambda x: x["published"], reverse=True)
    save(merged)
    print(f"Tổng: {len(merged)} tin (mới: {len(new_items)})")
    return merged, new_items


if __name__ == "__main__":
    crawl()
