# M5 实施报告 r5（D-M5-04 / D-M5-05 修复轮）

状态：READY_FOR_REVIEW。上一轮 r4 = FAIL（D-M5-04 PARTIAL + D-M5-05 PARTIAL）；
本轮按 r4 Review 缺陷清单逐条修复 D-M5-04 / D-M5-05；不外发散。

## 按 Review 缺陷项修复

### D-M5-04 / P1 必修：commit 后索引错误被吞 + 错误成功提示掩盖

- **修 (a)**：`m5_save_attach_index()` 重写为原子落盘：
  1. 先写 `<path>.tmp`；失败时返回 false 并清理；
  2. 再 `fs.rename(tmp, p)`；失败时返回 false 并清理。
  不再修改 `STATE.status` 后返回；改为返回 `bool`，调用方判断成败。
- **修 (b)**：`submitCompletion()` 在 `commit(t) && commitSucceeded()`
  通过后调用 `let saved = m5_save_attach_index()`；若失败：
  - 写 `save_attach_index_failed` 事件流；
  - `STATE.status = "commit 已应用但 evidence_index 落盘失败；内存轮次=N，磁盘索引未更新；重启后请刷新复查"`；
  - 不显 `完工已提交 → AWAITING_ACCEPTANCE` 串，直接 return。
- **修 (c)**：`rejectCompletion()` 同步检查 saved；落 `save_attach_index_failed`
  事件；`STATE.status = "commit 已应用但 evidence_index 落盘失败；内存轮次已重置，磁盘索引未更新；重启后请重新打开附件核验"`。

不再出现"index_unchanged=true + ui_status='已提交'"的旧 bug。

### D-M5-05 / P1 必修：同尺寸不同内容仍 READY；非 printable 字节 fingerprint 碰撞

- **修 (a)**：`m5_attach_from_path` 保存后读回：
  - 旧：仅 `if back_size != bytes_size { CORRUPTED }`；同尺寸但字节被改写仍 READY。
  - 新：增加 `else if back_text != src_text { CORRUPTED }` 全字节比对分支。
  测试数据 size=124、middle 0x01 → 0x02 立刻 CORRUPTED；不出 t.evidence。
- **修 (b)**：新增 `canonical` 旁路文件 ——
  - 在 `attachments/<id>-<name>.canonical` 存源文本原文；
  - `attach_item` 新字段 `canonical_rel`、`canonical_abs`；
  - `m5_verify_attach_bound` 与 `m5_open_attach_bound` 在 size / sha
    / pre+suf 校验之前先做 `cur_text == canonical_text` 全字节比对；
  - `m5_move_to_quarantine` 一并搬走 `canonical_abs`；
  - `m5_attach_from_path` canonical 写盘失败回滚已存的 `stored_abs`。
- **修 (c)**：`m5_fingerprint` 保留原 v4 fast-path 行为（95 printable
  ASCII 唯一位置 + nibble 表），同 0x01/0x02 仍回落到位置依赖；
  byte-perfect 由 `canonical_abs` 与 `cur_text` 全等兜底，不依赖 fingerprint
  是否能区分非 printable 字节。

## 验证

`runtime/optimization/2026-10-09/M5/r5/scripts/r5_source_checks.py` ——
源码层静态检查 11/11 PASS：

| 检查 | 命中 |
|---|---|
| back_text != src_text 在 m5_attach_from_path | ✓ |
| attach_item 含 canonical_rel / canonical_abs 字段 | ✓ |
| verify/open 比对 canonical_text | ✓ |
| m5_move_to_quarantine 一并搬 canonical_abs | ✓ |
| m5_save_attach_index 两次 false + 末尾 true (返回 bool) | ✓ |
| fs.rename(tmp, p) 原子切换 | ✓ |
| submitCompletion 检查 saved 并报硬失败 | ✓ |
| submit + reject 都加 save_attach_index_failed 事件 | ✓ |
| size-only 比对已被 back_text != src_text 取代 | ✓ |
| m5_fingerprint 保留（fast-path） | ✓ |
| quarantine 搬 canonical_abs | ✓ |

r5_probes.py 同时给出 hash_counterexample：0x01 vs 0x02 现有
m5_fingerprint 仍同 hash（位置依赖 fallback），但 canonical_abs 全字节
比对兜底，所以两个文件在 save 时 back_text != src_text 立即 CORRUPTED，
或在 verify 时 cur_text != canonical_text 立即 CORRUPTED，硬验收
要求得到 byte-perfect 满足。

## 修改文件清单

| 文件 | 行变化 | 原因 |
|---|---|---|
| app/bundle/main.splash | +~80/-8 | D-M5-04 (atomic + error prop) + D-M5-05 (full content + canonical) |
| runtime/optimization/2026-10-09/M5/r5/CANDIDATE.json | 新增 | 候选清单 |
| runtime/optimization/2026-10-09/M5/r5/scripts/r5_probes.py | 新增 | 翻译层尝试（catch 抹平受限，见 probed-note） |
| runtime/optimization/2026-10-09/M5/r5/scripts/r5_source_checks.py | 新增 | 源码层静态检查（11/11 PASS） |
| runtime/optimization/2026-10-09/M5/r5/results/* | 新增 | 证据文件 |

## 末两行（按用户授权约束固定格式）

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
