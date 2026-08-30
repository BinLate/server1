# Changelog

## [2026-08-30] - SimCity Optimization, PK & Dynamic AOI Upgrade

### Fixed
- **Lỗi Đồ Sát (Camp 5):** Sửa hàm `IsAttackableCamp` trong `libs/common.lua` để 2 người cùng bật Đồ Sát (5 vs 5) đánh được nhau thay vì bị tính là đồng minh.
- **Lỗi Lag & Đứng Im Tống Kim:** Giảm số lượng bot từ hơn 672 con xuống đúng 20 bot mỗi phe (40 bot tổng cộng: 1 Soái, 2 Đại Tướng, 3 Phó Tướng, 4 Hiệu Úy, 10 Binh Sĩ) trong `plugins/pchientranh.lua`.
- **Lỗi Máu Yếu / 1-Shot:** Gán đúng Level 95+ và gọi `SimGear:ApplyGearStats` cho toàn bộ bot trong `group_fighter.class.lua` và `sim.entity.lua` giúp bot có đúng 6,000 – 12,000+ HP và phòng thủ chuẩn.
- **Lỗi Encoding:** Chuẩn hóa toàn bộ 45 file Lua trong `simcity` về bảng mã `Windows-1258` thuần túy.

### Added
- **Dynamic AOI Lazy-Spawning Map Luyện Công:** Tự động spawn 15-25 Simbot theo cấp độ map khi có người chơi bước vào, và tự động hibernate (0% CPU) sau 2 phút người chơi rời map trong `plugins/pluyencong.lua`.
- **Tranh Bãi Train & Võ Mồm:** Tỷ lệ ngẫu nhiên 5-10% Simbot luyện công bật Đồ Sát (`Camp 5`), thét kênh chat và chém nhau kịch tính.
