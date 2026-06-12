# -*- coding: utf-8 -*-
"""
run_daily.py — Chạy toàn bộ pipeline: quét → phân loại → sinh dashboard.
Dùng cho cron hoặc GitHub Actions.
"""
import crawler
import classify
import build_dashboard


def main():
    print("=== 1/3 Quét nguồn tin ===")
    items, new_items = crawler.crawl()

    print("=== 2/3 Phân loại tin ===")
    classify.classify(items)
    crawler.save(items)

    print("=== 3/3 Sinh dashboard ===")
    build_dashboard.build()
    print("Hoàn tất.")


if __name__ == "__main__":
    main()
