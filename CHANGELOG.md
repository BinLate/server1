# Changelog

## [2026-08-30] - SimCity Optimization, PK & Dynamic AOI Upgrade

### Fixed
- **Lỗi Đồ Sát (Camp 5):** Sửa hàm `IsAttackableCamp` trong `libs/common.lua` để 2 người cùng bật Đồ Sát (5 vs 5) đánh được nhau thay vì bị tính là đồng minh.
- **Giới hạn an toàn Tống Kim (5 Tống / 5 Kim = 10 Bot):** Cố định cấu hình tập trung `TONGKIM_SIMBOT_PER_CAMP = 5` và `TONGKIM_SIMBOT_TOTAL = 10` trong `config.lua`, đồng bộ điều tiết trong `simtk.lua` và chuyển hướng toàn bộ các hàm spawn cũ trong `pchientranh.lua` để đảm bảo không vượt quá ngân sách CPU.
- **Lỗi Máu Yếu / 1-Shot:** Gán đúng Level 95+ và gọi `SimGear:ApplyGearStats` cho toàn bộ bot trong `group_fighter.class.lua` và `sim.entity.lua` giúp bot có đúng 6,000 – 12,000+ HP và phòng thủ chuẩn.
- **Lỗi Encoding:** Chuẩn hóa toàn bộ 45 file Lua trong `simcity` về bảng mã `Windows-1258` thuần túy.

### Added
- **Dynamic AOI Lazy-Spawning Map Luyện Công:** Tự động spawn 15-25 Simbot theo cấp độ map khi có người chơi bước vào, và tự động hibernate (0% CPU) sau 2 phút người chơi rời map trong `plugins/pluyencong.lua`.
- **Tranh Bãi Train & Võ Mồm:** Tỷ lệ ngẫu nhiên 5-10% Simbot luyện công bật Đồ Sát (`Camp 5`), thét kênh chat và chém nhau kịch tính.
