# -*- coding: utf-8 -*-
"""
CẤU HÌNH HỆ THỐNG — chỉnh sửa file này theo nhu cầu của bạn.
"""

# ============================================================
# 1. DANH SÁCH MÃ CỔ PHIẾU THEO DÕI
#    ticker -> các tên gọi/alias để nhận diện trong tiêu đề bài viết
#    Thêm/bớt mã tuỳ ý. Alias không phân biệt hoa thường.
# ============================================================
TICKERS = {
    "VIC": ["Vingroup"],
    "VHM": ["Vinhomes"],
    "VRE": ["Vincom Retail"],
    "VNM": ["Vinamilk"],
    "HPG": ["Hòa Phát", "Hoà Phát", "Hoa Phat"],
    "FPT": ["FPT Corp", "tập đoàn FPT"],
    "MWG": ["Thế Giới Di Động", "The Gioi Di Dong"],
    "VCB": ["Vietcombank"],
    "TCB": ["Techcombank"],
    "BID": ["BIDV"],
    "CTG": ["VietinBank"],
    "MBB": ["MB Bank", "Ngân hàng Quân đội"],
    "SSI": ["Chứng khoán SSI"],
    "VND": ["VNDirect", "VNDIRECT"],
    "NVL": ["Novaland"],
    "DIG": ["DIC Corp"],
    "PDR": ["Phát Đạt", "Phat Dat"],
    "HAG": ["Hoàng Anh Gia Lai", "HAGL"],
    "GVR": ["Cao su Việt Nam"],
    "MSN": ["Masan"],
    "SAB": ["Sabeco"],
    "GAS": ["PV GAS", "PV Gas"],
    "POW": ["PV Power"],
    "VJC": ["Vietjet"],
    "HVN": ["Vietnam Airlines"],
}

# ============================================================
# 2. NGUỒN TIN (RSS feeds)
#    source_type: "press" (báo chính thống) | "forum" (diễn đàn) | "social" (MXH)
#    Bạn có thể thêm bất kỳ RSS nào. Gợi ý:
#    - Diễn đàn XenForo (F319, VOZ...) thường có RSS dạng:
#        https://<domain>/forums/<tên-forum>/index.rss
#    - Google News RSS theo từ khoá (bắt được cả bài được index từ nhiều nơi):
#        https://news.google.com/rss/search?q=<từ+khoá>&hl=vi&gl=VN&ceid=VN:vi
# ============================================================
FEEDS = [
    # --- Báo chính thống ---
    {"name": "CafeF - Chứng khoán",        "url": "https://cafef.vn/thi-truong-chung-khoan.rss",                 "source_type": "press"},
    {"name": "CafeF - Doanh nghiệp",       "url": "https://cafef.vn/doanh-nghiep.rss",                           "source_type": "press"},
    {"name": "VnExpress - Kinh doanh",     "url": "https://vnexpress.net/rss/kinh-doanh.rss",                    "source_type": "press"},
    {"name": "Vietstock - Cổ phiếu",       "url": "https://vietstock.vn/830/chung-khoan/co-phieu.rss",           "source_type": "press"},
    {"name": "Tin nhanh chứng khoán",      "url": "https://www.tinnhanhchungkhoan.vn/rss/chung-khoan.rss",       "source_type": "press"},
    {"name": "Người Quan Sát - CK",        "url": "https://nguoiquansat.vn/rss/chung-khoan.rss",                 "source_type": "press"},

    # --- Diễn đàn (RSS công khai; chỉnh URL nếu diễn đàn đổi cấu trúc) ---
    {"name": "F319",                       "url": "https://f319.com/forums/-/index.rss",                         "source_type": "forum"},
    {"name": "VOZ - Tiền điện tử & CK",    "url": "https://voz.vn/f/diem-bao.33/index.rss",                      "source_type": "forum"},

    # --- Google News theo từng mã (bắt cả bài MXH/blog được Google index) ---
    # Được sinh tự động cho mỗi ticker trong TICKERS, xem crawler.py.
]

# Tự sinh feed Google News cho mỗi mã: "cổ phiếu <MÃ>"
ENABLE_GOOGLE_NEWS_PER_TICKER = True
GOOGLE_NEWS_TEMPLATE = (
    "https://news.google.com/rss/search?"
    "q=%22c%E1%BB%95%20phi%E1%BA%BFu%20{ticker}%22&hl=vi&gl=VN&ceid=VN:vi"
)

# ============================================================
# 3. TỪ KHOÁ "TIN ĐỒN" — bài chứa các từ này được ưu tiên đánh dấu
# ============================================================
RUMOR_KEYWORDS = [
    "tin đồn", "đồn đoán", "rò rỉ", "nghi vấn", "lan truyền",
    "chưa xác nhận", "úp mở", "râm ran", "xôn xao", "đính chính", "bác bỏ",
]

# ============================================================
# 4. CÀI ĐẶT KHÁC
# ============================================================
KEEP_DAYS = 14            # giữ tin trong bao nhiêu ngày
MAX_ITEMS_PER_FEED = 40   # đọc tối đa bao nhiêu bài mỗi feed mỗi lần chạy
REQUEST_TIMEOUT = 20      # giây
USE_CLAUDE_CLASSIFIER = True  # nếu có biến môi trường ANTHROPIC_API_KEY thì dùng AI
                              # để phân loại cảm xúc & mức xác thực; không có thì
                              # tự động dùng phân loại từ khoá (miễn phí).
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
