# Phase 06: Chat / giao dịch (sau MVP — không LLM trong MVP)
Status: ⬜ Pending
Dependencies: Phase 05 ổn định

## Objective

Social layer sau combat/progression/TK. **Không đưa LLM vào MVP.**

Thứ tự:

1. Chat template/local  
2. World chat  
3. PM  
4. Rao bán / mặc cả  
5. Optional LLM (không block main loop; gameplay OK khi provider chết)

## Requirements

### Functional
- [ ] Template chat đa dạng theo context (train/city/TK)
- [ ] World channel rate-limited (`SIMBOT_CHAT_COOLDOWN`)
- [ ] PM response rules (template)
- [ ] Rao bán / mặc cả scripted
- [ ] LLM optional, async, fail-open

### Non-Functional
- [ ] LLM tuyệt đối không block game tick
- [ ] Provider down → bot vẫn combat/train bình thường

## Implementation Steps
1. [ ] Audit `pchat.lua` / Phase D code
2. [ ] Template packs + cooldowns
3. [ ] World + PM
4. [ ] Trade dialogue state machine
5. [ ] Optional LLM adapter behind flag `SIMBOT_LLM_ENABLED=0`

## Files
- `plugins/pchat.lua`, `components/sim.fun.lua`, `config.lua`
- Chat data: `settings/global/vdk/simcity/chat.txt`

## Test Criteria
- [ ] Có chat thế giới mà không spam
- [ ] Tắt LLM: zero regression
- [ ] Bật LLM giả lập timeout: gameplay không đứng

---
Next Phase: [phase-07-living-world-polish.md](phase-07-living-world-polish.md)
