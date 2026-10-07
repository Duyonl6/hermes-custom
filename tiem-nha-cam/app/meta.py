"""Danh mục, khu vực — dùng chung cho app và seed."""

CATEGORIES = [
    # key, nhãn, icon (tên trong icons.html)
    ("mirrorless", "Mirrorless", "mirrorless"),
    ("dslr", "DSLR", "dslr"),
    ("compact", "Compact", "compact"),
    ("film", "Máy film", "film"),
    ("action", "Action cam", "action"),
    ("cam360", "Camera 360°", "cam360"),
    ("drone", "Flycam", "drone"),
    ("vlog", "Vlog & Gimbal", "vlog"),
    ("lens", "Ống kính", "lens"),
]

CATEGORY_LABELS = {key: label for key, label, _ in CATEGORIES}

# Toạ độ gần đúng của khu vực (bản đồ chỉ hiện vị trí xấp xỉ — địa chỉ cụ thể gửi sau khi đặt).
# Tên phường theo địa giới mới từ 01/07/2025.
LOCATIONS = {
    "hn-hoankiem": ("Hà Nội", "Phường Hoàn Kiếm", 21.0287, 105.8524),
    "hn-cuanam": ("Hà Nội", "Phường Cửa Nam", 21.0245, 105.8445),
    "hn-badinh": ("Hà Nội", "Phường Ba Đình", 21.0405, 105.8390),
    "hn-ngocha": ("Hà Nội", "Phường Ngọc Hà", 21.0360, 105.8180),
    "hn-giangvo": ("Hà Nội", "Phường Giảng Võ", 21.0265, 105.8225),
    "hn-caugiay": ("Hà Nội", "Phường Cầu Giấy", 21.0330, 105.7930),
    "hn-nghiado": ("Hà Nội", "Phường Nghĩa Đô", 21.0470, 105.7980),
    "hn-yenhoa": ("Hà Nội", "Phường Yên Hòa", 21.0205, 105.7945),
    "hn-tayho": ("Hà Nội", "Phường Tây Hồ", 21.0640, 105.8235),
    "hn-hadong": ("Hà Nội", "Phường Hà Đông", 20.9715, 105.7780),
    "hn-dongda": ("Hà Nội", "Phường Đống Đa", 21.0150, 105.8270),
    "hcm-saigon": ("TP. Hồ Chí Minh", "Phường Sài Gòn", 10.7769, 106.7009),
    "hcm-benthanh": ("TP. Hồ Chí Minh", "Phường Bến Thành", 10.7720, 106.6980),
    "hcm-tandinh": ("TP. Hồ Chí Minh", "Phường Tân Định", 10.7905, 106.6905),
    "hcm-ankhanh": ("TP. Hồ Chí Minh", "Phường An Khánh (Thảo Điền)", 10.8030, 106.7350),
    "hcm-binhthanh": ("TP. Hồ Chí Minh", "Phường Bình Thạnh", 10.8050, 106.7090),
    "dn-haichau": ("Đà Nẵng", "Phường Hải Châu", 16.0680, 108.2205),
    "dn-sontra": ("Đà Nẵng", "Phường Sơn Trà", 16.0760, 108.2440),
    "dn-hoian": ("Đà Nẵng", "Phường Hội An", 15.8801, 108.3380),
    "ld-dalat": ("Lâm Đồng", "Phường Xuân Hương - Đà Lạt", 11.9404, 108.4583),
    "lc-sapa": ("Lào Cai", "Phường Sa Pa", 22.3364, 103.8438),
    "kh-nhatrang": ("Khánh Hòa", "Phường Nha Trang", 12.2388, 109.1967),
    "qn-baichay": ("Quảng Ninh", "Phường Bãi Cháy", 20.9560, 107.0480),
    "ag-phuquoc": ("An Giang", "Đặc khu Phú Quốc", 10.2270, 103.9640),
}

CITIES = sorted({city for city, *_ in LOCATIONS.values()}, key=lambda c: (c not in {"Hà Nội", "TP. Hồ Chí Minh"}, c))

# Kiểu ảnh minh họa mặc định theo danh mục (khi chủ thuê tạo tin mới)
DEFAULT_ART = {
    "mirrorless": "mirrorless", "dslr": "dslr", "compact": "compact", "film": "film", "action": "action",
    "cam360": "cam360", "drone": "drone", "vlog": "vlog", "lens": "lens",
}
BRAND_KEYS = {"sony": "sony", "canon": "canon", "fujifilm": "fujifilm", "fuji": "fujifilm", "nikon": "nikon",
              "gopro": "gopro", "dji": "dji", "insta360": "insta360", "olympus": "olympus"}


def art_for(category: str, brand: str) -> str:
    """Sinh mã ảnh minh họa cho tin do chủ thuê tạo (vd. "drone:dji:grey")."""
    kind = DEFAULT_ART.get(category, "mirrorless")
    b = BRAND_KEYS.get(brand.strip().lower(), "generic")
    color = {"drone": "grey", "film": "silver"}.get(category, "black")
    if kind == "mirrorless" and b == "fujifilm":
        kind, color = "retro", "silver"
    return f"{kind}:{b}:{color}"
