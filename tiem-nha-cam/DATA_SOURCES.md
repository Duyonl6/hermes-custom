# Nguồn dữ liệu (khảo sát 10/2026)

Dữ liệu demo dựa trên thông tin công khai. **Chủ thuê, người thuê và đánh giá đều là nhân vật minh họa.**
Riêng "Tiệm nhà Cam" là brand của chủ dự án. Không tin đăng nào đại diện cho shop có thật.

## Giá thuê theo ngày (từ website các shop cho thuê tại VN)

| Thiết bị | Giá tham khảo | Nguồn |
|---|---|---|
| Sony A7 IV | 500k (HN) – 700k – 730k – 750k | [Kam Media](https://kammedia.vn/cho-thue-may-anh-thiet-bi-quay-phim-ha-noi/), [Thiết bị Gáo](https://thietbigao.com/san-pham/chi-tiet-san-pham/sony-alpha-a7-iv.html), [Meta Mobile](https://thietbichothue.vn/dich-vu-cho-thue-may-anh/), [Tiệm Chụp Ảnh](https://tiemchupanh.com/san-pham/sony-a7-mark-iv/), [Chothuestudio](https://chothuestudio.com/product/cho-thue-sony-a7-mark-iv-sieu-re/) |
| Canon R6 Mark II | 670k – 700k | [Tiệm Chụp Ảnh](https://tiemchupanh.com/san-pham/cho-thue-body-canon-r6-mark-ii/) |
| Fujifilm X-T5 | 450k | [WinWinStore](https://www.winwinstore.vn/tin-tuc/dv-cho-thue-may-anh-ong-kinh-phu-kien/) |
| Sony ZV-E10 | 210k – 300k | [Camerahouse](https://camerahouse.vn/products/body-sony-zv-e10), [Thuecam](https://thuecam.com/khu-vuc/bien-hoa) |
| GoPro HERO13 Black | 200k, cọc 1 triệu | [TADA](https://vienthongtada.com.vn/cho-thue-gopro-hero-12-va-13-thue-camera-hanh-trinh-thue-action-camera-chinh-hang-gia-re-uy-tin-tai-ha-noi-hai-phong-tp-ho-chi-minh), [FesCam](https://fescamera.com/san-pham/cho-thue-gopro-hero-13-black/) |
| Insta360 X5 | 178k – 250k | [SmartTech360](https://smarttech360.com.vn/thue-insta360-x5-tp-hcm), [Thuecam](https://thuecam.com/thiet-bi/insta360-x5-combo) |
| Insta360 X4 | 140k – 200k | [Chothueaz](https://chothueaz.vn/cho-thue-camera-hanh-dong-insta360-x4-one-x4-chinh-hang-tai-ha-noi-hai-phong-tp-ho-chi-minh-uy-tin-chinh-hang-gia-re), [FesCam](https://fescamera.com/san-pham/cho-thue-insta360-x4-one-x4/) |
| DJI Osmo Action 5 Pro | 150k – 250k | [SmartTech360](https://smarttech360.com.vn/dich-vu-thue-dji-action-5-pocket-3-tphcm), [TADA](https://vienthongtada.com.vn/cho-thue-camera-hanh-dong-dji-action-4-va-action-5-pro-adventure-combo-tai-ha-noi-hai-phong-tp-ho-chi-minh-cho-thue-hang-chinh-hang-voi-gia-re) |
| DJI Osmo Pocket 3 | 139k – 200k | [VH Digital](https://vhdigital.vn/cho-thue-dji-pocket-3-12682.html), [TokyoCamera](https://tokyocamera.vn/thue-dji-osmo-pocket-3/) |
| DJI Mini 4 Pro | 590k – 600k (HN), 350k (HCM) | [DJI Service](https://djiservice.vn/dich-vu-thue-flycam/), [NAZA](https://naza.vn/cho-thue-flycam/), [Flycamgiare](https://flycamgiare.vn/cho-thue-flycam-ha-noi/), [Camerahouse](https://camerahouse.vn/products/flycam-dji-mavic-mini-4-pro) |
| DJI Mavic 3 Pro | 1,3 triệu | [DJI Service](https://djiservice.vn/dich-vu-thue-flycam/), [TokyoCamera](https://tokyocamera.vn/cho-thue-flycam-dji-tai-ha-noi/) |
| DJI Neo | 140k – 250k | [Lee-Cam](https://leecam.vn/cho-thue-flycam-dji-neo-danh-cho-nhu-cau-bay-don-gian), [Thuê Nhanh](https://thuenhanh.vn/products/cho-thue-flycam-dji-neo) |

Các máy còn lại (Air 3S, Mavic 4 Pro, Mini 5 Pro, Avata 2, Flip, Nikon Z6 III, máy film, ống kính…) chưa
có giá thuê công khai. Giá được **ước tính** theo giá trị máy (~2–3%/ngày) và các máy cùng phân khúc. Mỗi
mục trong `seed/catalog.py` đều ghi rõ nguồn hoặc nhãn "ước tính".

**Chính sách tham khảo:**

- Cọc CCCD kèm 30–50% giá trị máy ([Hanoigimbal](https://chothuegimbal.com/cho-thue-body-may-anh-may-quay/page/2/)).
- 1 ngày = 24 giờ ([Tiệm Chụp Ảnh](https://tiemchupanh.com/san-pham/sony-a7-mark-iv/)).
- Trả trễ phụ thu 30% trong 6 giờ đầu ([Máy ảnh BMT](https://www.mayanhbmt.com/cho-thue-may-anh-ong-kinh-va-phu-kien-gia-re-chat-luong-tai-bmt/)).

## Giá bán tham khảo (để tính cọc)

- GoPro HERO13: ~9,09 triệu ([TokyoCamera](https://tokyocamera.vn/san-pham/gopro-hero-13-black/))
- DJI Flip RC 2: 16,25 triệu ([FPT Shop](https://fptshop.com.vn/phu-kien/flycam-dji-flip-rc-2-gl))
- Osmo Pocket 3 Creator Combo: 15,89 triệu ([Di Động Việt](https://didongviet.vn/thiet-bi-cong-nghe/camera-dji-osmo-pocket-3-creator-combo.html))
- DJI Air 3S lúc ra mắt: ~27,44 triệu ([Sforum](https://cellphones.com.vn/sforum/dji-air-3s-ra-mat))
- Sony A7 IV lúc ra mắt: 59,99 triệu ([VnReview](https://vnreview.vn/threads/sony-alpha-7-iv-co-gia-60-trieu-tai-viet-nam-nhan-dat-hang-tu-ngay-mai.26897/latest))

## Thông số kỹ thuật

Theo công bố của hãng (Sony, Canon, Nikon, Fujifilm, GoPro, DJI, Insta360). Riêng thông số DJI Mini 5 Pro
(1 inch 50MP, 4K120, 36 phút, dưới 250 g, LiDAR) đối chiếu với [CineD](https://www.cined.com/dji-mini-5-pro-released-250g-drone-with-1-inch-type-50mp-sensor-4k-up-to-120fps-and-rotatable-gimbal/)
và [TechRadar](https://www.techradar.com/cameras/drones/dji-mini-5-pro-review).

## Quy định bay flycam

- Miễn giấy phép bay cho máy dưới 0,25 kg bay giải trí, ngoài khu vực cấm và trong tầm nhìn: Luật Phòng
  không nhân dân 2024, khoản 3 Điều 30; NĐ 288/2025/NĐ-CP, hiệu lực 05/11/2025
  ([Thư viện Pháp luật](https://thuvienphapluat.vn/hoi-dap-phap-luat/flycam-duoi-250g-co-can-xin-giay-phep-khong-138069792.html),
  [LuatVietnam](https://luatvietnam.vn/tin-van-ban-moi/dieu-kien-doi-voi-nguoi-dieu-khien-flycam-tu-05-11-2025-186-105203-article.html)).
- Đăng ký, mã định danh từ 20/7/2026 theo Thông tư 78/2026/TT-BCA
  ([FPT Shop](https://fptshop.com.vn/tin-tuc/for-gamers/cach-dang-ky-ma-dinh-danh-cho-drone-flycam-210166),
  [Doanh nghiệp Hội nhập](https://doanhnghiephoinhap.vn/tu-207-drone-va-flycam-tren-toan-quoc-bat-buoc-phai-gan-ma-dinh-danh-141431.html)).
- Phạt tới 40 triệu đồng theo NĐ 282/2025/NĐ-CP
  ([VOV](https://vov.vn/xa-hoi/bay-flycam-drone-sai-quy-dinh-co-the-bi-phat-toi-40-trieu-dong-tich-thu-thiet-bi-post1308893.vov)).

Đây là thông tin tổng hợp từ báo chí, không phải tư vấn pháp lý.

## Địa giới hành chính

Tên phường dùng theo sắp xếp từ 01/07/2025: Hà Nội theo NQ 1656/NQ-UBTVQH15, TP.HCM theo NQ
1685/NQ-UBTVQH15 ([GHTK](https://ghtk.vn/blog/ha-noi-sau-sap-nhap/),
[Thư viện Pháp luật](https://thuvienphapluat.vn/phap-luat-nha-dat/danh-sach-168-xa-phuong-moi-tphcm-sau-sap-nhap-la-nhung-xa-phuong-nao-5524.html)).
Toạ độ trên bản đồ là gần đúng, đúng với thiết kế: chỉ hiện vị trí xấp xỉ trước khi đơn được đặt.
