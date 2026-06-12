# 📡 Radar Tin Đồn — Công ty đại chúng Việt Nam

Hệ thống **tự động chạy hàng ngày**: quét tin tức & tin đồn về các công ty niêm
yết VN từ báo chính thống, diễn đàn, Google News; phân loại cảm xúc và mức độ
xác thực; xuất ra dashboard web — **mỗi tin đều có link gốc** để bấm vào đọc.

## Cấu trúc

```
config.py            # ⚙️ Chỉnh ở đây: mã CK theo dõi, nguồn RSS, từ khoá
crawler.py           # Quét RSS, nhận diện mã CK, khử trùng lặp
classify.py          # Gán nhãn cảm xúc / xác thực (heuristic hoặc Claude API)
build_dashboard.py   # Sinh docs/index.html (dashboard tĩnh)
run_daily.py         # Chạy cả pipeline
data/items.json      # Kho tin (giữ 14 ngày)
docs/index.html      # Dashboard — mở bằng trình duyệt hoặc đưa lên GitHub Pages
.github/workflows/daily.yml  # Lịch chạy tự động trên GitHub Actions
```

## Cách 1 (khuyên dùng): Tự chạy hàng ngày bằng GitHub Actions — MIỄN PHÍ, không cần server

1. Tạo một repository mới trên GitHub (private hoặc public đều được, nhưng
   GitHub Pages miễn phí cần repo **public**).
2. Đưa toàn bộ thư mục này lên repo:
   ```bash
   git init && git add . && git commit -m "init"
   git remote add origin https://github.com/<bạn>/<repo>.git
   git push -u origin main
   ```
3. Vào **Settings → Pages**: chọn *Deploy from a branch* → branch `main`,
   thư mục `/docs` → Save.
4. Vào tab **Actions** → bật workflow → bấm *Run workflow* để chạy thử lượt đầu.
5. Xong! Mỗi sáng **7:30** (và 12:30) giờ VN, hệ thống tự quét tin và cập nhật
   dashboard tại: `https://<bạn>.github.io/<repo>/`

*(Tuỳ chọn)* Để dùng AI phân loại chính xác hơn: **Settings → Secrets and
variables → Actions → New secret** tên `ANTHROPIC_API_KEY`. Không có key, hệ
thống tự dùng phân loại từ khoá (miễn phí, vẫn hoạt động tốt).

## Cách 2: Chạy trên máy của bạn với cron

```bash
pip install -r requirements.txt
python run_daily.py            # chạy thử một lượt
open docs/index.html           # xem dashboard

# Đặt lịch hàng ngày 7:30 sáng (Linux/Mac):
crontab -e
# thêm dòng:
30 7 * * * cd /đường/dẫn/vn-rumor-radar && python run_daily.py
```

Trên Windows: dùng Task Scheduler trỏ tới `python run_daily.py`.

## Tuỳ biến

- **Thêm/bớt mã cổ phiếu**: sửa `TICKERS` trong `config.py` (kèm alias tên
  công ty để bắt cả bài không ghi mã).
- **Thêm nguồn**: thêm RSS vào `FEEDS`. Diễn đàn nền XenForo (F319, VOZ...)
  thường có RSS dạng `https://<domain>/forums/<tên>/index.rss`. Google News
  RSS theo từ khoá bắt được rất nhiều bài từ các trang nhỏ.
- **Thời gian giữ tin / lịch chạy**: `KEEP_DAYS` trong `config.py`; giờ chạy
  trong `.github/workflows/daily.yml` (cron theo giờ UTC, VN = UTC+7).

## Giới hạn cần biết

- **Nhóm kín Facebook, Zalo, Telegram không quét được** — nội dung này không
  công khai và việc thu thập tự động vi phạm điều khoản của các nền tảng.
  Hệ thống bù lại bằng Google News RSS (bắt bài công khai được index) và RSS
  diễn đàn mở.
- Cấu trúc RSS của các trang có thể thay đổi theo thời gian; feed lỗi sẽ được
  bỏ qua (không làm sập pipeline) và in cảnh báo trong log — kiểm tra log
  Actions định kỳ để cập nhật URL.
- ⚠️ **Tin đồn chưa kiểm chứng có thể sai lệch hoặc bị thao túng giá.** Luôn
  đối chiếu công bố thông tin chính thức trên HOSE/HNX/website doanh nghiệp.
  Hệ thống này chỉ là công cụ theo dõi, không phải khuyến nghị đầu tư.
