"""Dữ liệu catalog thiết bị dùng để seed.

- Thông số kỹ thuật: theo công bố của hãng (xem DATA_SOURCES.md).
- `rent_ref`: giá thuê/ngày tham khảo từ các shop cho thuê thật ở VN (khảo sát 10/2026).
  `rent_src` ghi nguồn; mục nào ghi "ước tính" là do chưa có giá công khai, được nội suy theo
  giá trị máy (~2–3%/ngày) và các máy cùng phân khúc.
- `retail`: giá trị thiết bị tham khảo (VND) — dùng để tính tiền cọc.
"""

from app.meta import CATEGORIES, LOCATIONS  # noqa: F401 — re-export cho seed

PRODUCTS = {
    # ------------------------------------------------------------ mirrorless
    "sony-a7iv": dict(
        category="mirrorless", brand="Sony", model="Alpha A7 IV", art="mirrorless:sony:black", weight=658,
        retail=47_000_000, rent_ref=(500_000, 750_000),
        rent_src="Kam Media (HN) 500k · Meta Mobile/Thiết bị Gáo 700k · TCA 730k · Chothuestudio 750k",
        specs=[("Cảm biến", "Full-frame 33MP Exmor R BSI"), ("Video", "4K 60p 10-bit 4:2:2, S-Cinetone"),
               ("Chống rung", "IBIS 5 trục, 5.5 stop"), ("Lấy nét", "759 điểm AF, Eye AF người/động vật/chim"),
               ("Màn hình", "3.0\" xoay lật cảm ứng"), ("Pin", "NP-FZ100 (~580 ảnh/pin)"), ("Ngàm", "Sony E"),
               ("Trọng lượng", "658 g (kèm pin, thẻ)")],
        blurb="Con máy \"làm được mọi thứ\": chụp cưới, sự kiện, quay YouTube 4K 10-bit đều ổn. "
              "Eye AF bám mắt cực chắc, màn xoay lật tiện quay vlog, pin NP-FZ100 trâu.",
    ),
    "sony-a7iii": dict(
        category="mirrorless", brand="Sony", model="Alpha A7 III", art="mirrorless:sony:black", weight=650,
        retail=30_000_000, rent_ref=(350_000, 450_000), rent_src="ước tính (đời trước A7 IV)",
        specs=[("Cảm biến", "Full-frame 24.2MP BSI"), ("Video", "4K 30p (oversample 6K), S-Log3"),
               ("Chống rung", "IBIS 5 trục, 5 stop"), ("Lấy nét", "693 điểm Phase-detect"),
               ("Pin", "NP-FZ100 (~710 ảnh/pin)"), ("Ngàm", "Sony E"), ("Trọng lượng", "650 g")],
        blurb="Full-frame giá mềm cho người mới lên đời: màu da đẹp, pin cực trâu, thừa sức chụp kỷ yếu, "
              "chân dung, du lịch.",
    ),
    "sony-zve10": dict(
        category="mirrorless", brand="Sony", model="ZV-E10", art="mirrorless:sony:black", weight=343,
        retail=15_000_000, rent_ref=(210_000, 300_000), rent_src="Camerahouse (HCM) 300k · ITECAM 210k",
        specs=[("Cảm biến", "APS-C 24.2MP"), ("Video", "4K 30p (oversample 6K), không crop"),
               ("Màn hình", "Lật cạnh, chuyên vlog"), ("Âm thanh", "Mic 3 capsule + chống gió"),
               ("Pin", "NP-FW50"), ("Ngàm", "Sony E"), ("Trọng lượng", "343 g")],
        blurb="Máy vlog quốc dân: nhỏ gọn, màn lật cạnh, nút Product Showcase lấy nét sản phẩm cực nhanh — "
              "hợp review đồ, quay TikTok, livestream.",
    ),
    "canon-r6ii": dict(
        category="mirrorless", brand="Canon", model="EOS R6 Mark II", art="mirrorless:canon:black", weight=670,
        retail=48_000_000, rent_ref=(650_000, 700_000), rent_src="Tiệm Chụp Ảnh/TCA (HCM) 670–700k",
        specs=[("Cảm biến", "Full-frame 24.2MP"), ("Video", "4K 60p oversample 6K, 10-bit C-Log3"),
               ("Chống rung", "IBIS tới 8 stop"), ("Tốc độ", "40 fps màn trập điện tử"),
               ("Lấy nét", "Dual Pixel AF II, nhận diện người/thú/xe"), ("Pin", "LP-E6NH"), ("Ngàm", "Canon RF"),
               ("Trọng lượng", "670 g")],
        blurb="Màu Canon trứ danh, da người lên cực đẹp. Chống rung 8 stop cầm tay quay vẫn mượt, "
              "AF bắt cô dâu chú rể trong ánh sáng yếu rất ngọt.",
    ),
    "canon-r8": dict(
        category="mirrorless", brand="Canon", model="EOS R8", art="mirrorless:canon:black", weight=461,
        retail=30_000_000, rent_ref=(400_000, 450_000), rent_src="ước tính (TCA có cho thuê, chưa công khai giá)",
        specs=[("Cảm biến", "Full-frame 24.2MP"), ("Video", "4K 60p oversample 6K"),
               ("Lấy nét", "Dual Pixel AF II"), ("Pin", "LP-E17"), ("Ngàm", "Canon RF"), ("Trọng lượng", "461 g")],
        blurb="Full-frame nhẹ nhất nhà Canon — cảm biến như R6 II trong thân hình gọn, đi du lịch cả ngày không mỏi tay.",
    ),
    "canon-r50": dict(
        category="mirrorless", brand="Canon", model="EOS R50", art="mirrorless:canon:white", weight=375,
        retail=17_000_000, rent_ref=(220_000, 280_000), rent_src="ước tính",
        specs=[("Cảm biến", "APS-C 24.2MP"), ("Video", "4K 30p oversample 6K"), ("Màn hình", "Xoay lật"),
               ("Pin", "LP-E17"), ("Ngàm", "Canon RF"), ("Trọng lượng", "375 g")],
        blurb="Máy nhỏ xinh, menu thân thiện cho người mới. Chế độ A+ chụp đâu đẹp đó, hợp đi chơi, chụp bạn bè.",
    ),
    "nikon-z6iii": dict(
        category="mirrorless", brand="Nikon", model="Z6 III", art="mirrorless:nikon:black", weight=760,
        retail=55_000_000, rent_ref=(600_000, 700_000), rent_src="ước tính",
        specs=[("Cảm biến", "Full-frame 24.5MP partially-stacked"), ("Video", "6K 60p N-RAW, 4K 120p"),
               ("Chống rung", "IBIS tới 8 stop"), ("Kính ngắm", "EVF 5.76M điểm, 4000 nits"),
               ("Pin", "EN-EL15c"), ("Ngàm", "Nikon Z"), ("Trọng lượng", "760 g")],
        blurb="Quái vật video tầm trung: 6K RAW nội bộ, 4K120 slow-motion, kính ngắm sáng nhất phân khúc.",
    ),
    "fuji-xt5": dict(
        category="mirrorless", brand="Fujifilm", model="X-T5", art="retro:fujifilm:silver", weight=557,
        retail=40_000_000, rent_ref=(450_000, 500_000), rent_src="WinWinStore (HCM) 450k",
        specs=[("Cảm biến", "APS-C 40.2MP X-Trans CMOS 5 HR"), ("Video", "6.2K 30p 10-bit"),
               ("Chống rung", "IBIS 7 stop"), ("Giả lập film", "19 film simulation (Classic Chrome, Nostalgic Neg…)"),
               ("Pin", "NP-W235 (~580 ảnh)"), ("Ngàm", "Fujifilm X"), ("Trọng lượng", "557 g")],
        blurb="Vặn dial chụp như máy film, ảnh JPEG ra màu \"ăn liền\" không cần hậu kỳ. Có sẵn công thức màu "
              "Kodak Portra, Classic Neg cài trong máy.",
    ),
    "fuji-xs20": dict(
        category="mirrorless", brand="Fujifilm", model="X-S20", art="mirrorless:fujifilm:black", weight=491,
        retail=30_000_000, rent_ref=(330_000, 380_000), rent_src="ước tính",
        specs=[("Cảm biến", "APS-C 26.1MP"), ("Video", "6.2K 30p, 4K 60p 10-bit"), ("Chống rung", "IBIS 7 stop"),
               ("Pin", "NP-W235 (~750 ảnh)"), ("Ngàm", "Fujifilm X"), ("Trọng lượng", "491 g")],
        blurb="Báng cầm sâu, pin to, chế độ Vlog riêng — lựa chọn cân bằng giữa chụp ảnh màu Fuji và quay video.",
    ),
    # ----------------------------------------------------------------- dslr
    "canon-5div": dict(
        category="dslr", brand="Canon", model="EOS 5D Mark IV", art="dslr:canon:black", weight=890,
        retail=35_000_000, rent_ref=(400_000, 500_000), rent_src="ước tính",
        specs=[("Cảm biến", "Full-frame 30.4MP"), ("Video", "4K 30p (crop 1.74x)"), ("Lấy nét", "61 điểm AF"),
               ("Kính ngắm", "Quang học 100%"), ("Pin", "LP-E6N (~900 ảnh)"), ("Ngàm", "Canon EF"),
               ("Trọng lượng", "890 g")],
        blurb="Ngựa thồ của dân chụp cưới suốt nhiều năm: bền, pin trâu, kính ngắm quang học, hệ ống kính EF khổng lồ.",
    ),
    # -------------------------------------------------------------- compact
    "fuji-x100vi": dict(
        category="compact", brand="Fujifilm", model="X100VI", art="compact:fujifilm:silver", weight=521,
        retail=45_000_000, rent_ref=(450_000, 650_000), rent_src="ước tính (shop Đà Nẵng niêm yết ~650k/lượt)",
        specs=[("Cảm biến", "APS-C 40.2MP X-Trans CMOS 5 HR"), ("Ống kính", "23mm f/2 (tương đương 35mm)"),
               ("Chống rung", "IBIS 6 stop"), ("Kính ngắm", "Hybrid OVF/EVF"), ("Giả lập film", "20 film simulation"),
               ("Video", "6.2K 30p"), ("Trọng lượng", "521 g")],
        blurb="Máy \"đu trend\" hot nhất mạng xã hội: nhỏ gọn, đẹp như máy film, màu Fuji chụp phố, cafe, du lịch "
              "cực chill. Hàng hiếm, nên đặt sớm cuối tuần.",
    ),
    "canon-g7xiii": dict(
        category="compact", brand="Canon", model="PowerShot G7 X Mark III", art="compact:canon:black", weight=304,
        retail=18_000_000, rent_ref=(200_000, 280_000), rent_src="ước tính",
        specs=[("Cảm biến", "1 inch 20.1MP stacked"), ("Ống kính", "24–100mm tương đương, f/1.8–2.8"),
               ("Video", "4K 30p, livestream YouTube"), ("Màn hình", "Lật 180° selfie"), ("Trọng lượng", "304 g")],
        blurb="Bỏ túi quần được, màn lật selfie, ảnh da mịn màu Canon — \"máy của idol\" để vlog, chụp concert, du lịch.",
    ),
    # ----------------------------------------------------------------- film
    "canon-ae1p": dict(
        category="film", brand="Canon", model="AE-1 Program + FD 50mm f/1.8", art="film:canon:silver", weight=575,
        retail=6_000_000, rent_ref=(120_000, 180_000), rent_src="ước tính",
        specs=[("Loại", "SLR film 35mm"), ("Ống kính", "Canon FD 50mm f/1.8"), ("Tốc độ", "2 giây – 1/1000 giây"),
               ("Chế độ", "Program / ưu tiên tốc độ / manual"), ("Pin", "4LR44 6V"), ("Trọng lượng", "575 g (body)")],
        blurb="Huyền thoại máy film cho người mới: có chế độ Program tự đo sáng. Đã bảo dưỡng, đo sáng chuẩn, "
              "seal gương mới. Không kèm phim — có bán Kodak Gold/Ultramax tại chỗ.",
    ),
    "olympus-mju2": dict(
        category="film", brand="Olympus", model="mju-II (Stylus Epic)", art="compact:olympus:black", weight=135,
        retail=8_000_000, rent_ref=(120_000, 180_000), rent_src="ước tính",
        specs=[("Loại", "Point & shoot film 35mm"), ("Ống kính", "35mm f/2.8"), ("Chống nước", "Chống tia nước"),
               ("Pin", "CR123A"), ("Trọng lượng", "135 g")],
        blurb="Máy film bỏ túi được săn lùng nhất: ống kính 35mm f/2.8 sắc, flash tự động — chỉ việc ngắm và bấm.",
    ),
    # --------------------------------------------------------------- action
    "gopro-hero13": dict(
        category="action", brand="GoPro", model="HERO13 Black", art="action:gopro:black", weight=159,
        retail=9_100_000, rent_ref=(180_000, 200_000), rent_src="TADA (HN/ĐN/HP/HCM) 200k, cọc 1tr · FesCam từ 100k",
        specs=[("Video", "5.3K 60p, 4K 120p, 2.7K 240p"), ("Ảnh", "27MP"), ("Chống rung", "HyperSmooth 6.0, khóa chân trời 360°"),
               ("Chống nước", "10 m không cần vỏ"), ("Pin", "Enduro 1900 mAh"), ("Trọng lượng", "159 g")],
        blurb="Action cam đi đâu cũng được: lặn biển, phượt xe máy, trượt tuyết. Gắn mũ bảo hiểm, ngực, ghi-đông đều có ngàm.",
    ),
    "gopro-hero12": dict(
        category="action", brand="GoPro", model="HERO12 Black", art="action:gopro:black", weight=154,
        retail=7_500_000, rent_ref=(130_000, 170_000), rent_src="ước tính",
        specs=[("Video", "5.3K 60p, 4K 120p"), ("Ảnh", "27MP, HDR"), ("Chống rung", "HyperSmooth 6.0"),
               ("Chống nước", "10 m"), ("Pin", "Enduro 1720 mAh"), ("Trọng lượng", "154 g")],
        blurb="Đời trước HERO13 nhưng vẫn quay đẹp xuất sắc, giá thuê dễ chịu cho chuyến đi biển dài ngày.",
    ),
    "dji-action5pro": dict(
        category="action", brand="DJI", model="Osmo Action 5 Pro", art="action:dji:graphite", weight=146,
        retail=9_500_000, rent_ref=(150_000, 250_000), rent_src="SmartTech360 (HCM) 150–180k · TADA 250k",
        specs=[("Cảm biến", "1/1.3 inch, 13.5 stop DR"), ("Video", "4K 120p, 10-bit D-Log M"),
               ("Chống nước", "20 m không cần vỏ"), ("Bộ nhớ trong", "47 GB"), ("Pin", "1950 mAh, tới 4 giờ"),
               ("Màn hình", "2 màn OLED cảm ứng trước/sau"), ("Trọng lượng", "146 g")],
        blurb="Pin quay tới 4 tiếng, lặn 20 m không cần vỏ, quay đêm đỡ noise hơn hẳn — hợp đi tour, lặn ngắm san hô.",
    ),
    # --------------------------------------------------------------- cam360
    "insta360-x5": dict(
        category="cam360", brand="Insta360", model="X5", art="cam360:insta360:black", weight=200,
        retail=14_000_000, rent_ref=(178_000, 250_000), rent_src="SmartTech360 (HCM) 250k · ITECAM 178–220k",
        specs=[("Video", "8K 30p 360°, 5.7K 60p"), ("Cảm biến", "2 × 1/1.28 inch"), ("Ống kính", "Thay được khi trầy"),
               ("Chống nước", "15 m"), ("Pin", "2400 mAh, tới 185 phút"), ("Trọng lượng", "200 g")],
        blurb="Quay 360° rồi chọn góc sau — gậy selfie \"tàng hình\" như có người quay hộ. Đi phượt, đi concert cực đã.",
    ),
    "insta360-x4": dict(
        category="cam360", brand="Insta360", model="X4", art="cam360:insta360:black", weight=203,
        retail=11_000_000, rent_ref=(140_000, 200_000), rent_src="chothueaz/TADA 200k · ITECAM từ 140k",
        specs=[("Video", "8K 30p 360°, 4K 100p"), ("Chống nước", "10 m"), ("Pin", "2290 mAh, tới 135 phút"),
               ("Trọng lượng", "203 g")],
        blurb="Camera 360 8K giá thuê mềm, hiệu ứng gậy tàng hình, bullet time, AI tự dựng clip trên app.",
    ),
    # ---------------------------------------------------------------- drones
    "dji-mini4pro": dict(
        category="drone", brand="DJI", model="Mini 4 Pro", art="drone:dji:grey", weight=249,
        retail=20_000_000, rent_ref=(350_000, 600_000),
        rent_src="DJI Service (HN) 590k · NAZA/Flycamgiare (HN) 600k · Camerahouse (HCM) 350k",
        specs=[("Trọng lượng", "Dưới 249 g"), ("Cảm biến", "1/1.3 inch 48MP"), ("Video", "4K 60p HDR, 4K 100p"),
               ("Cảm biến tránh vật cản", "Đa hướng"), ("Thời gian bay", "34 phút/pin"), ("Truyền hình", "O4, tới 20 km (FCC)"),
               ("Quay dọc", "True Vertical xoay gimbal 90°")],
        blurb="Flycam dưới 250 g — nhóm được miễn giấy phép bay khi bay giải trí đúng quy định. Tránh vật cản đa hướng, "
              "ActiveTrack bám theo xe/người, người mới bay vẫn an toàn.",
    ),
    "dji-mini5pro": dict(
        category="drone", brand="DJI", model="Mini 5 Pro", art="drone:dji:grey", weight=249,
        retail=25_000_000, rent_ref=(650_000, 750_000), rent_src="ước tính (máy mới, chưa có giá thuê công khai)",
        specs=[("Trọng lượng", "Dưới 250 g"), ("Cảm biến", "1 inch 50MP, f/1.8"), ("Video", "4K 60p HDR, 4K 120p, 10-bit D-Log M"),
               ("Gimbal", "Xoay 225°, quay dọc không crop"), ("Tránh vật cản", "Đa hướng + LiDAR"),
               ("Thời gian bay", "36 phút/pin"), ("Bộ nhớ trong", "42 GB")],
        blurb="Cảm biến 1 inch trong thân máy dưới 250 g: quay hoàng hôn, thành phố đêm sạch noise. LiDAR giúp bay tối an toàn hơn.",
    ),
    "dji-air3s": dict(
        category="drone", brand="DJI", model="Air 3S", art="drone:dji:grey", weight=724,
        retail=27_400_000, rent_ref=(750_000, 900_000), rent_src="ước tính (giá bán ~27,4tr lúc ra mắt)",
        specs=[("Camera", "Kép: 1 inch 50MP + tele 70mm 48MP"), ("Video", "4K 60p HDR, 4K 120p"),
               ("Thời gian bay", "45 phút/pin"), ("Tránh vật cản", "Đa hướng + LiDAR trước"),
               ("Truyền hình", "O4, tới 20 km (FCC)"), ("Trọng lượng", "724 g")],
        blurb="Hai camera cho hai kiểu khung hình: góc rộng phong cảnh và tele 70mm nén hậu cảnh cực điện ảnh.",
    ),
    "dji-mavic4pro": dict(
        category="drone", brand="DJI", model="Mavic 4 Pro", art="drone:dji:graphite", weight=1063,
        retail=58_000_000, rent_ref=(1_500_000, 1_800_000), rent_src="ước tính (AGS Tech: liên hệ)",
        specs=[("Camera chính", "Hasselblad 4/3 inch 100MP"), ("Camera phụ", "Tele 70mm 48MP + tele 168mm 50MP"),
               ("Video", "6K 60p HDR, 4K 120p"), ("Gimbal", "Infinity xoay 360°"), ("Thời gian bay", "51 phút/pin"),
               ("Truyền hình", "O4+, tới 30 km (FCC)"), ("Trọng lượng", "1063 g")],
        blurb="Flagship cho TVC, phim tài liệu, bất động sản. Ba camera, 6K HDR, gimbal xoay 360° cho góc máy không giới hạn.",
    ),
    "dji-mavic3pro": dict(
        category="drone", brand="DJI", model="Mavic 3 Pro", art="drone:dji:graphite", weight=958,
        retail=45_000_000, rent_ref=(1_300_000, 1_300_000), rent_src="DJI Service / DanCamera / TokyoCamera (HN) 1,3tr",
        specs=[("Camera chính", "Hasselblad 4/3 inch 20MP"), ("Camera phụ", "Tele 70mm 48MP + tele 166mm 12MP"),
               ("Video", "5.1K 50p, 4K 60p, Apple ProRes (bản Cine)"), ("Thời gian bay", "43 phút/pin"),
               ("Trọng lượng", "958 g")],
        blurb="Ba camera Hasselblad màu chuẩn, quen thuộc với ekip quay sự kiện & du lịch. Pin 43 phút thoải mái canh nắng.",
    ),
    "dji-avata2": dict(
        category="drone", brand="DJI", model="Avata 2 (Fly More Combo)", art="fpv:dji:black", weight=377,
        retail=25_000_000, rent_ref=(800_000, 1_000_000), rent_src="ước tính (Flycam Sky từng cho thuê Avata đời 1: 3tr/ngày)",
        specs=[("Loại", "FPV có lồng bảo vệ cánh"), ("Cảm biến", "1/1.3 inch 12MP"), ("Video", "4K 60p, góc 155°"),
               ("Điều khiển", "Goggles 3 + RC Motion 3"), ("Thời gian bay", "23 phút/pin"), ("Trọng lượng", "377 g")],
        blurb="Đeo kính bay như chim: lượn qua cổng làng, lách giữa rừng thông. Điều khiển bằng chuyển động tay, dễ hơn FPV truyền thống.",
    ),
    "dji-neo": dict(
        category="drone", brand="DJI", model="Neo", art="mini_guard:dji:white", weight=135,
        retail=5_000_000, rent_ref=(140_000, 250_000), rent_src="Lee-Cam 250k · ITECAM từ 140k",
        specs=[("Trọng lượng", "135 g"), ("Cảm biến", "1/2 inch 12MP"), ("Video", "4K 30p, chống rung EIS"),
               ("Cất cánh", "Từ lòng bàn tay, không cần tay cầm"), ("Thời gian bay", "18 phút/pin"),
               ("Chế độ", "QuickShots: Dronie, Circle, Rocket, Spotlight")],
        blurb="Selfie drone siêu nhẹ: thả trên tay là bay, tự quay vòng quanh bạn rồi đáp lại về tay. Không cần biết lái.",
    ),
    "dji-flip": dict(
        category="drone", brand="DJI", model="Flip", art="mini_guard:dji:grey", weight=249,
        retail=16_250_000, rent_ref=(400_000, 500_000), rent_src="ước tính (giá bán bản RC 2: 16,25tr)",
        specs=[("Trọng lượng", "249 g"), ("Cảm biến", "1/1.3 inch 48MP"), ("Video", "4K 60p HDR, 4K 100p"),
               ("Thiết kế", "Gập gọn, lồng bảo vệ cánh toàn phần"), ("Thời gian bay", "31 phút/pin")],
        blurb="Lồng bảo vệ cánh toàn phần nên bay gần người vẫn yên tâm — hợp quay nhóm bạn, team building, check-in.",
    ),
    # ------------------------------------------------------------ vlog/gimbal
    "dji-pocket3": dict(
        category="vlog", brand="DJI", model="Osmo Pocket 3 Creator Combo", art="vlog:dji:black", weight=179,
        retail=15_900_000, rent_ref=(139_000, 200_000),
        rent_src="VH Digital 179k (139k từ 5 ngày) · SmartTech360 150k · TokyoCamera 200k",
        specs=[("Cảm biến", "1 inch CMOS"), ("Video", "4K 120p, 10-bit D-Log M"), ("Gimbal", "3 trục cơ học"),
               ("Màn hình", "2\" OLED xoay ngang/dọc"), ("Pin", "1300 mAh, tới 166 phút"), ("Trọng lượng", "179 g")],
        blurb="\"Máy quay túi áo\" cho vlogger: gimbal 3 trục mượt như trượt, xoay màn là chuyển quay dọc TikTok. "
              "Combo có mic không dây DJI Mic 2.",
    ),
    "dji-rs4": dict(
        category="vlog", brand="DJI", model="RS 4 Gimbal", art="gimbal:dji:black", weight=1066,
        retail=12_000_000, rent_ref=(200_000, 280_000), rent_src="ước tính",
        specs=[("Tải trọng", "3 kg"), ("Pin", "Tới 12 giờ"), ("Tính năng", "Quay dọc native, khóa trục tự động"),
               ("Trọng lượng", "~1.07 kg")],
        blurb="Gimbal cho máy mirrorless + ống zoom: quay cưới, quay sự kiện, cảnh dolly mượt mà như có ray.",
    ),
    # ------------------------------------------------------------------ lens
    "sony-2470gm2": dict(
        category="lens", brand="Sony", model="FE 24-70mm f/2.8 GM II", art="lens:sony:black", weight=695,
        retail=48_000_000, rent_ref=(300_000, 400_000), rent_src="ước tính",
        specs=[("Tiêu cự", "24–70 mm"), ("Khẩu độ", "f/2.8 – f/22"), ("Lấy nét", "4 motor XD Linear"),
               ("Filter", "82 mm"), ("Ngàm", "Sony E (full-frame)"), ("Trọng lượng", "695 g")],
        blurb="Ống zoom \"chân ái\" của dân sự kiện: nhẹ hơn đời cũ, nét căng từ tâm ra rìa, lấy nét nhanh và êm khi quay.",
    ),
    "canon-rf2470": dict(
        category="lens", brand="Canon", model="RF 24-70mm f/2.8L IS USM", art="lens:canon:black", weight=900,
        retail=50_000_000, rent_ref=(300_000, 400_000), rent_src="ước tính",
        specs=[("Tiêu cự", "24–70 mm"), ("Khẩu độ", "f/2.8 – f/22"), ("Chống rung", "IS 5 stop"),
               ("Filter", "82 mm"), ("Ngàm", "Canon RF"), ("Trọng lượng", "900 g")],
        blurb="Ống L viền đỏ có chống rung — kết hợp IBIS của R6 II quay cầm tay rất đầm.",
    ),
}

INCLUDED = {
    "mirrorless": ["Body máy", "2 pin + sạc đôi", "Thẻ nhớ SD 128GB V60", "Dây đeo", "Túi chống sốc", "Khăn + bóng thổi bụi"],
    "dslr": ["Body máy", "2 pin + sạc", "Thẻ nhớ 128GB", "Dây đeo", "Túi máy"],
    "compact": ["Máy ảnh", "2 pin + sạc", "Thẻ nhớ 64GB", "Dây đeo tay", "Túi đựng"],
    "film": ["Máy film", "Pin dự phòng", "Dây đeo da", "Hướng dẫn lắp phim (in sẵn)"],
    "action": ["Máy quay", "3 pin + dock sạc 3 cổng", "Thẻ nhớ 128GB", "Gậy selfie 3 khúc", "Ngàm mũ bảo hiểm + ngực", "Phao tay nổi"],
    "cam360": ["Camera 360", "2 pin + sạc", "Thẻ nhớ 128GB", "Gậy tàng hình 114 cm", "Túi bảo vệ ống kính"],
    "drone": ["Flycam + tay điều khiển", "3 pin + hub sạc", "Cánh dự phòng", "Thẻ nhớ 128GB", "Bộ filter ND", "Balo đựng"],
    "vlog": ["Thiết bị", "Pin/tay cầm pin", "Thẻ nhớ 128GB", "Tripod mini", "Túi đựng"],
    "lens": ["Ống kính", "Nắp trước/sau", "Loa che nắng", "Filter UV", "Túi ống kính"],
}


# Chủ thuê (nhân vật demo, trừ "Tiệm nhà Cam" — brand của chủ dự án)
HOSTS = [
    dict(key="tiemnhacam", name="Tiệm nhà Cam", email="cam@demo.vn", loc="hn-hadong", superhost=1, verified=1, response=15,
         bio="Tiệm nhỏ cho thuê máy ảnh, máy quay cho các bạn sinh viên và content creator ở Hà Nội. "
             "Máy được vệ sinh cảm biến sau mỗi lượt thuê, có hướng dẫn dùng tận tình qua Zalo."),
    dict(key="minhquan", name="Minh Quân", email="minhquan@demo.vn", loc="hn-badinh", superhost=1, verified=1, response=30,
         bio="Photographer chụp cưới 8 năm, dùng hệ Sony. Cho thuê lại máy nhàn rỗi trong tuần, máy được bảo dưỡng định kỳ."),
    dict(key="lananh", name="Lan Anh Studio", email="lananh@demo.vn", loc="hn-tayho", superhost=0, verified=1, response=60,
         bio="Studio chụp ảnh nhỏ bên Hồ Tây. Mê máy Fuji và máy film — thuê máy kèm tư vấn công thức màu."),
    dict(key="hoangphi", name="Hoàng Phi", email="hoangphi@demo.vn", loc="hn-dongda", superhost=1, verified=1, response=20,
         bio="Pilot flycam có Giấy phép điều khiển bay. Bàn giao máy kèm hướng dẫn bay an toàn và các khu vực cấm bay ở Hà Nội."),
    dict(key="ducanh", name="Đức Anh", email="ducanh@demo.vn", loc="hn-caugiay", superhost=0, verified=1, response=90,
         bio="Quay phim tự do, hệ Canon. Nhận máy ở Cầu Giấy hoặc giao tận nơi nội thành."),
    dict(key="thaovy", name="Thảo Vy", email="thaovy@demo.vn", loc="hn-hoankiem", superhost=0, verified=1, response=45,
         bio="Content creator mảng du lịch. Cho thuê đồ vlog mình dùng hằng ngày, có mẹo quay TikTok tặng kèm."),
    dict(key="saigongear", name="Sài Gòn Gear", email="saigongear@demo.vn", loc="hcm-benthanh", superhost=1, verified=1, response=10,
         bio="Kho thiết bị quay chụp trung tâm Quận 1 cũ, mở cửa 8h–22h. Có xuất hóa đơn cho doanh nghiệp."),
    dict(key="ngoctram", name="Ngọc Trâm", email="ngoctram@demo.vn", loc="hcm-ankhanh", superhost=1, verified=1, response=25,
         bio="Mình là film photographer ở Thảo Điền. Máy film đều được test cuộn trước khi cho thuê."),
    dict(key="khangdrone", name="Khang Drone", email="khang@demo.vn", loc="hcm-binhthanh", superhost=0, verified=1, response=40,
         bio="Đội bay flycam sự kiện & bất động sản. Cho thuê máy tự bay hoặc kèm pilot."),
    dict(key="tuankiet", name="Tuấn Kiệt", email="tuankiet@demo.vn", loc="hcm-tandinh", superhost=0, verified=0, response=120,
         bio="Dân phượt, đi Hà Giang 7 lần. Cho thuê đồ action cam đã đi cùng mình qua nhiều cung đường."),
    dict(key="haidang", name="Hải Đăng", email="haidang@demo.vn", loc="dn-sontra", superhost=1, verified=1, response=15,
         bio="Hướng dẫn viên lặn ở Sơn Trà. Đồ action cam đủ phụ kiện lặn, giao tận khách sạn ven biển Đà Nẵng."),
    dict(key="maihoian", name="Mai Hội An", email="mai@demo.vn", loc="dn-hoian", superhost=1, verified=1, response=20,
         bio="Nhà mình ở phố cổ. Cho thuê máy để bạn tự chụp đèn lồng, sông Hoài — có map các góc chụp đẹp."),
    dict(key="dalatlens", name="Đà Lạt Lens", email="dalat@demo.vn", loc="ld-dalat", superhost=0, verified=1, response=35,
         bio="Đà Lạt mù sương rất ăn ảnh! Giao máy tận homestay khu trung tâm."),
    dict(key="vanthang", name="Văn Thắng", email="vanthang@demo.vn", loc="lc-sapa", superhost=0, verified=1, response=60,
         bio="Porter kiêm thợ ảnh ở Sa Pa. Có sạc dự phòng và túi chống ẩm cho các tour trekking."),
    dict(key="phuclam", name="Phúc Lâm", email="phuclam@demo.vn", loc="kh-nhatrang", superhost=1, verified=1, response=15,
         bio="Cho thuê đồ quay lặn biển Nha Trang — có vỏ chống nước dự phòng và filter đỏ cho cảnh dưới nước."),
    dict(key="thanhtung", name="Thanh Tùng", email="thanhtung@demo.vn", loc="ag-phuquoc", superhost=0, verified=0, response=90,
         bio="Sống ở Phú Quốc, giao máy tận resort khu Bãi Trường và Dương Đông."),
    dict(key="quanghuy", name="Quang Huy", email="quanghuy@demo.vn", loc="qn-baichay", superhost=0, verified=1, response=50,
         bio="Thợ quay du thuyền vịnh Hạ Long. Lưu ý: bay flycam trên vịnh cần xin phép, mình hướng dẫn thủ tục."),
]

# (host_key, product_key, location_key, giá/ngày, tiêu đề, gói/kit, instant_book, giao tận nơi, phí giao, tình trạng)
LISTINGS = [
    ("tiemnhacam", "fuji-x100vi", "hn-hadong", 550_000, "Fujifilm X100VI bạc — máy film kỹ thuật số hot trend", "Kèm công thức màu Kodak Portra", 1, 1, 30_000, "Như mới"),
    ("tiemnhacam", "canon-g7xiii", "hn-hadong", 230_000, "Canon G7 X Mark III — vlog & chụp concert", "Kèm 2 pin + tay cầm mini", 1, 1, 30_000, "Rất tốt"),
    ("tiemnhacam", "dji-pocket3", "hn-hadong", 180_000, "DJI Osmo Pocket 3 Creator Combo + DJI Mic 2", "Creator Combo", 1, 1, 30_000, "Như mới"),
    ("tiemnhacam", "insta360-x5", "hn-hadong", 230_000, "Insta360 X5 8K + gậy tàng hình — quay phượt", "Kèm gậy tàng hình 114 cm", 1, 1, 30_000, "Như mới"),
    ("tiemnhacam", "olympus-mju2", "hn-hadong", 150_000, "Olympus mju-II — máy film bỏ túi huyền thoại", "", 0, 1, 30_000, "Tốt"),
    ("minhquan", "sony-a7iv", "hn-badinh", 600_000, "Sony A7 IV body — sẵn sàng chụp cưới, sự kiện", "Body + 2 pin", 1, 1, 40_000, "Rất tốt"),
    ("minhquan", "sony-2470gm2", "hn-badinh", 350_000, "Sony FE 24-70mm f/2.8 GM II — ống zoom quốc dân", "", 1, 1, 40_000, "Như mới"),
    ("minhquan", "sony-a7iii", "hn-badinh", 380_000, "Sony A7 III body — full-frame giá mềm", "Body + 3 pin", 0, 1, 40_000, "Tốt"),
    ("lananh", "fuji-xt5", "hn-tayho", 480_000, "Fujifilm X-T5 bạc + XF 18-55mm — màu Fuji ăn liền", "Kèm lens XF 18-55mm f/2.8-4", 0, 0, 0, "Như mới"),
    ("lananh", "fuji-xs20", "hn-tayho", 350_000, "Fujifilm X-S20 — chụp màu film, quay vlog 6.2K", "Kèm lens XC 15-45mm", 0, 0, 0, "Rất tốt"),
    ("lananh", "canon-ae1p", "hn-tayho", 150_000, "Canon AE-1 Program + FD 50mm — máy film cho người mới", "", 0, 0, 0, "Tốt"),
    ("hoangphi", "dji-mini4pro", "hn-dongda", 590_000, "DJI Mini 4 Pro Fly More — dưới 250g, 3 pin", "Fly More Combo (RC 2, 3 pin)", 1, 1, 50_000, "Như mới"),
    ("hoangphi", "dji-air3s", "hn-dongda", 850_000, "DJI Air 3S Fly More — camera kép 1 inch + tele", "Fly More Combo (RC 2, 3 pin)", 0, 1, 50_000, "Như mới"),
    ("hoangphi", "dji-mavic3pro", "hn-dongda", 1_300_000, "DJI Mavic 3 Pro — 3 camera Hasselblad cho ekip quay", "Fly More Combo (RC Pro)", 0, 1, 50_000, "Rất tốt"),
    ("hoangphi", "dji-avata2", "hn-dongda", 900_000, "DJI Avata 2 FPV — đeo kính bay như chim", "Fly More (Goggles 3, RC Motion 3, 3 pin)", 0, 0, 0, "Rất tốt"),
    ("ducanh", "canon-r6ii", "hn-caugiay", 680_000, "Canon EOS R6 Mark II — màu da Canon, IBIS 8 stop", "Body + 2 pin LP-E6NH", 1, 1, 40_000, "Như mới"),
    ("ducanh", "canon-rf2470", "hn-caugiay", 350_000, "Canon RF 24-70mm f/2.8L IS — ống L viền đỏ", "", 1, 1, 40_000, "Rất tốt"),
    ("ducanh", "dji-rs4", "hn-caugiay", 230_000, "DJI RS 4 gimbal — quay cưới, quay sự kiện mượt", "Kèm tay cầm pin BG30", 1, 1, 40_000, "Rất tốt"),
    ("thaovy", "canon-g7xiii", "hn-hoankiem", 250_000, "Canon G7 X III đen — máy vlog của idol", "", 1, 0, 0, "Như mới"),
    ("thaovy", "sony-zve10", "hn-hoankiem", 260_000, "Sony ZV-E10 + lens kit — quay TikTok, review", "Kèm lens 16-50mm + mic Rode", 1, 0, 0, "Rất tốt"),
    ("thaovy", "dji-neo", "hn-hoankiem", 220_000, "DJI Neo — selfie drone bay từ lòng bàn tay", "Fly More Combo (3 pin)", 1, 0, 0, "Như mới"),
    ("saigongear", "sony-a7iv", "hcm-benthanh", 700_000, "Sony A7 IV + 28-70mm — kho Quận 1, nhận máy 15 phút", "Kèm lens kit FE 28-70mm", 1, 1, 35_000, "Như mới"),
    ("saigongear", "canon-r6ii", "hcm-benthanh", 670_000, "Canon R6 Mark II body — có xuất hóa đơn VAT", "Body + 2 pin", 1, 1, 35_000, "Như mới"),
    ("saigongear", "nikon-z6iii", "hcm-benthanh", 650_000, "Nikon Z6 III — 6K RAW, 4K120 cho quay MV", "Body + 2 pin EN-EL15c", 1, 1, 35_000, "Như mới"),
    ("saigongear", "canon-5div", "hcm-benthanh", 450_000, "Canon 5D Mark IV — DSLR bền bỉ chụp cưới", "Body + 3 pin + grip", 1, 1, 35_000, "Tốt"),
    ("ngoctram", "fuji-x100vi", "hcm-ankhanh", 600_000, "Fujifilm X100VI — dạo Thảo Điền chụp chill", "", 0, 1, 30_000, "Như mới"),
    ("ngoctram", "olympus-mju2", "hcm-ankhanh", 160_000, "Olympus mju-II đã test cuộn — tặng 1 cuộn Kodak", "Tặng 1 cuộn Kodak ColorPlus 200", 0, 1, 30_000, "Rất tốt"),
    ("ngoctram", "canon-r50", "hcm-ankhanh", 250_000, "Canon R50 trắng + 18-45mm — dễ dùng cho người mới", "Kèm lens kit 18-45mm", 1, 1, 30_000, "Như mới"),
    ("khangdrone", "dji-mini4pro", "hcm-binhthanh", 400_000, "DJI Mini 4 Pro — giá tốt Sài Gòn, kèm RC 2", "DJI RC 2, 3 pin", 1, 1, 40_000, "Rất tốt"),
    ("khangdrone", "dji-mavic4pro", "hcm-binhthanh", 1_600_000, "DJI Mavic 4 Pro Creator Combo — 6K HDR cho TVC", "Creator Combo (RC Pro 2, 512GB)", 0, 1, 40_000, "Như mới"),
    ("khangdrone", "dji-mini5pro", "hcm-binhthanh", 700_000, "DJI Mini 5 Pro — cảm biến 1 inch, LiDAR bay đêm", "Fly More Combo", 0, 1, 40_000, "Như mới"),
    ("tuankiet", "gopro-hero13", "hcm-tandinh", 190_000, "GoPro HERO13 Black — bộ phượt đầy đủ ngàm", "Kèm ngàm xe máy + mũ bảo hiểm", 1, 1, 30_000, "Rất tốt"),
    ("tuankiet", "dji-action5pro", "hcm-tandinh", 180_000, "DJI Osmo Action 5 Pro — pin 4 tiếng quay cả ngày", "Adventure Combo", 1, 1, 30_000, "Như mới"),
    ("tuankiet", "insta360-x4", "hcm-tandinh", 170_000, "Insta360 X4 — 8K 360°, hiệu ứng gậy tàng hình", "", 1, 1, 30_000, "Tốt"),
    ("haidang", "gopro-hero13", "dn-sontra", 200_000, "GoPro HERO13 + vỏ lặn 60m — lặn Sơn Trà", "Kèm vỏ lặn Super Suit + filter đỏ", 1, 1, 0, "Như mới"),
    ("haidang", "insta360-x5", "dn-sontra", 250_000, "Insta360 X5 — quay 360° Bà Nà, Cầu Rồng", "", 1, 1, 0, "Như mới"),
    ("haidang", "dji-flip", "dn-sontra", 450_000, "DJI Flip — flycam có lồng cánh, bay biển Mỹ Khê", "Fly More Combo (RC 2)", 1, 1, 0, "Như mới"),
    ("maihoian", "fuji-x100vi", "dn-hoian", 650_000, "X100VI chụp phố cổ Hội An — kèm map góc chụp", "Kèm map 20 góc chụp đẹp", 1, 1, 0, "Như mới"),
    ("maihoian", "canon-ae1p", "dn-hoian", 140_000, "Canon AE-1 Program — chụp film đèn lồng Hội An", "", 1, 1, 0, "Tốt"),
    ("maihoian", "dji-pocket3", "dn-hoian", 190_000, "Osmo Pocket 3 — vlog phố cổ về đêm", "Creator Combo", 1, 1, 0, "Rất tốt"),
    ("dalatlens", "fuji-xt5", "ld-dalat", 450_000, "Fujifilm X-T5 — săn mây Đà Lạt màu film", "Kèm lens XF 18-55mm", 1, 1, 20_000, "Rất tốt"),
    ("dalatlens", "dji-mini4pro", "ld-dalat", 550_000, "DJI Mini 4 Pro — bay đồi chè, rừng thông", "Fly More Combo", 0, 1, 20_000, "Rất tốt"),
    ("dalatlens", "canon-r50", "ld-dalat", 230_000, "Canon R50 — chụp homestay, cafe Đà Lạt", "Kèm lens 18-45mm", 1, 1, 20_000, "Như mới"),
    ("vanthang", "gopro-hero13", "lc-sapa", 200_000, "GoPro HERO13 — trekking Fansipan, bản Cát Cát", "Kèm 3 pin + túi chống ẩm", 1, 1, 0, "Rất tốt"),
    ("vanthang", "dji-mini4pro", "lc-sapa", 600_000, "DJI Mini 4 Pro — ruộng bậc thang mùa lúa chín", "Fly More Combo", 0, 1, 0, "Rất tốt"),
    ("phuclam", "gopro-hero13", "kh-nhatrang", 190_000, "GoPro HERO13 — lặn Hòn Mun, Nha Trang", "Kèm vỏ lặn + filter đỏ", 1, 1, 0, "Như mới"),
    ("phuclam", "dji-action5pro", "kh-nhatrang", 170_000, "Osmo Action 5 Pro — lặn 20m không cần vỏ", "Adventure Combo", 1, 1, 0, "Như mới"),
    ("thanhtung", "gopro-hero12", "ag-phuquoc", 150_000, "GoPro HERO12 — snorkeling Hòn Thơm", "Kèm phao tay + gậy nổi", 1, 1, 0, "Tốt"),
    ("thanhtung", "dji-neo", "ag-phuquoc", 200_000, "DJI Neo — selfie drone ở resort Phú Quốc", "", 1, 1, 0, "Như mới"),
    ("quanghuy", "dji-air3s", "qn-baichay", 850_000, "DJI Air 3S — quay du thuyền vịnh Hạ Long", "Fly More Combo", 0, 1, 0, "Như mới"),
    ("quanghuy", "gopro-hero13", "qn-baichay", 190_000, "GoPro HERO13 — chèo kayak hang Sửng Sốt", "Kèm ngàm kayak", 1, 1, 0, "Rất tốt"),
]

RENTERS = [
    "Nguyễn Hà My", "Trần Đức Huy", "Lê Phương Thảo", "Phạm Gia Bảo", "Hoàng Thu Trang", "Vũ Minh Khôi",
    "Đặng Ngọc Ánh", "Bùi Tiến Dũng", "Đỗ Khánh Linh", "Ngô Quang Vinh", "Dương Mỹ Duyên", "Lý Hoàng Nam",
    "Phan Thanh Tâm", "Võ Nhật Minh", "Trịnh Bảo Ngọc", "Mai Anh Tuấn", "Hồ Thị Yến", "Chu Văn Long",
    "Tạ Minh Châu", "Lâm Gia Hân", "Kiều Đức Thịnh", "Quách Tuệ Nhi", "Đinh Công Hậu", "La Thùy Dương",
]

# Câu đánh giá mẫu (demo) — ghép ngẫu nhiên mở đầu + thân + kết để đa dạng
REVIEW_OPENERS = [
    "Lần đầu thuê máy online mà trải nghiệm quá ổn.", "Thuê cho chuyến đi 3 ngày của nhóm.", "Đã thuê ở đây lần thứ hai.",
    "Thuê gấp buổi tối mà vẫn được hỗ trợ.", "Thuê để chụp kỷ yếu cho lớp.", "Mình thuê để quay vlog du lịch.",
    "Cả nhà đi chơi nên thuê thêm máy cho tiện.", "Thuê để thử trước khi quyết định mua.", "", "", "",
]
REVIEW_CLOSERS = [
    "Recommend cho mọi người!", "Chắc chắn sẽ quay lại.", "10 điểm không có nhưng.", "Cảm ơn chủ thuê nhiều!",
    "Sẽ giới thiệu bạn bè.", "Đáng đồng tiền.", "", "", "",
]
REVIEW_SNIPPETS = {
    "common": [
        "Chủ thuê nhiệt tình, hướng dẫn rất kỹ cách dùng trước khi giao máy.",
        "Máy sạch sẽ, đúng như mô tả, phụ kiện đầy đủ.",
        "Giao nhận nhanh gọn, cọc hoàn lại ngay khi trả máy.",
        "Giá hợp lý so với chất lượng máy.",
        "Rep tin nhắn cực nhanh, hỗ trợ cả lúc mình đang ở xa.",
        "Thủ tục đơn giản, chỉ cần CCCD và cọc là nhận máy luôn.",
        "Đặt đêm khuya vẫn được xác nhận, sáng ra lấy máy ngay.",
        "Giao máy tận khách sạn đúng giờ hẹn.",
        "Có biên bản bàn giao rõ ràng, chụp ảnh tình trạng máy hai bên nên rất yên tâm.",
        "Trả máy trễ 1 tiếng do kẹt xe mà chủ thuê vẫn vui vẻ không tính phí.",
        "Chủ thuê còn sạc đầy pin và format sẵn thẻ nhớ.",
        "Máy còn rất mới, gần như không có vết xước.",
    ],
    "camera": [
        "Ảnh ra màu đẹp, cảm biến sạch không một vết bụi.",
        "Chụp kỷ yếu cả ngày pin vẫn còn dư, thẻ nhớ tốc độ cao nên chụp liên tiếp không bị đơ.",
        "Lần đầu dùng máy này mà được chỉ setting nhanh nên ảnh lên rất ổn.",
        "Màu film giả lập quá đỉnh, ảnh không cần chỉnh vẫn đẹp.",
        "Lấy nét mắt bắt cực nhanh, chụp trẻ con chạy nhảy vẫn nét.",
        "Được chia sẻ thêm công thức màu nên ảnh lên tông rất chill.",
        "Chụp đêm phố cổ mà noise vẫn rất ít.",
    ],
    "action": [
        "Mang đi lặn ngắm san hô, quay rõ nét, không bị vào nước chút nào.",
        "Gắn mũ bảo hiểm đi Hà Giang 4 ngày, video chống rung mượt khó tin.",
        "Pin dự phòng nhiều nên quay thoải mái cả ngày.",
        "Ngàm gắn đủ loại, gậy selfie chắc chắn.",
        "Quay slow-motion cảnh sóng biển đẹp xuất sắc.",
    ],
    "drone": [
        "Được hướng dẫn bay kỹ và nhắc các khu vực cấm bay, rất yên tâm.",
        "Máy bay ổn định, gió khá to vẫn giữ vị trí tốt. Video 4K lên rất nét.",
        "Pin đủ 3 quả, sạc hub tiện. Quay hoàng hôn trên đồi chè đẹp mê.",
        "Tay điều khiển có màn hình sẵn nên không cần dùng điện thoại.",
        "ActiveTrack bám theo xe máy rất chuẩn, cảnh quay như phim.",
    ],
    "vlog": [
        "Quay vlog đi bộ mà mượt như dùng gimbal lớn, màn xoay quay dọc tiện cực.",
        "Mic kèm theo thu tiếng rõ, đỡ phải mang thêm đồ.",
        "Nhỏ gọn bỏ túi áo, đi đâu cũng mang theo được.",
        "Quay đêm vẫn sáng và ít noise hơn điện thoại nhiều.",
    ],
    "lens": [
        "Ống nét căng, lấy nét nhanh, không có mốc hay rơ zoom.",
        "Thuê kèm body cùng chủ nên được giảm giá, quá ok.",
        "Xóa phông đẹp, chụp chân dung rất ngọt.",
    ],
}
