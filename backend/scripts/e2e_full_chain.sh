#!/usr/bin/env bash
# OctoSense 端到端：报修 → 接单 → 设备绑定 → 预约 → 开工 → 记录 → 完工 → 退回 → 完工 → 验收
# 用法：先启动 uvicorn 在端口 8713，再跑本脚本

set -euo pipefail
API="http://127.0.0.1:8713/api/octosense/v1"
REPORTER="u-reporter-1"
TECH="u-tech-1"
MGR="u-manager"

J() { python3 -c "import sys,json;d=json.load(sys.stdin);print(json.dumps(d,ensure_ascii=False))"; }

echo "[1] create_draft"
TID=$(curl -sS -X POST "$API/tasks" -H "X-Actor-Id: $REPORTER" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-c1","project_id":"prj-A","problem_text":"空调不制冷","contact_name":"张三"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['task_id'])")
echo "  task=$TID"

echo "[2] confirm_draft v=1"
curl -sS -X POST "$API/tasks/$TID/confirm" -H "X-Actor-Id: $REPORTER" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-cf1","expected_version":1}' | J

echo "[3] accept_task v=2 (tech_1)"
curl -sS -X POST "$API/tasks/$TID/accept" -H "X-Actor-Id: $TECH" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-ac1","expected_version":2}' | J

echo "[4] bind-asset v=3"
curl -sS -X POST "$API/tasks/$TID/bind-asset" -H "X-Actor-Id: $REPORTER" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-bd1","expected_version":3,"asset_id":"as-a-1"}' | J

echo "[5] propose_appointment v=4"
START=$(python3 -c "import time;print(int(time.time()*1000)+3600000)")
END=$(python3 -c "import time;print(int(time.time()*1000)+7200000)")
curl -sS -X POST "$API/tasks/$TID/appointments" -H "X-Actor-Id: $TECH" -H "Content-Type: application/json" \
  -d "{\"idempotency_key\":\"e2e-pp1\",\"expected_version\":4,\"start_at_ms\":$START,\"end_at_ms\":$END}" | J

echo "[6] confirm_appointment v=5"
AID=$(curl -sS "$API/tasks/$TID" -H "X-Actor-Id: $REPORTER" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['appointments'][-1]['appointment_id'])")
curl -sS -X POST "$API/tasks/$TID/appointments/$AID/confirm" -H "X-Actor-Id: $REPORTER" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-ca1","expected_version":5}' | J

echo "[7] start_progress v=6"
curl -sS -X POST "$API/tasks/$TID/start" -H "X-Actor-Id: $TECH" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-sp1","expected_version":6}' | J

echo "[8] record_progress v=7"
curl -sS -X POST "$API/tasks/$TID/progress" -H "X-Actor-Id: $TECH" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-rp1","expected_version":7,"note":"拆外壳完成"}' | J

# T19：完工前必须上传至少 1 条 READY 证据；QUARANTINED 不算。
# evidence 不 bump task.version，此时 task.version 仍是 8（record_progress 已推进到 8）
echo "[8a] upload_evidence (T19)"
python3 -c "open('/tmp/e2e-evidence-1.jpg','wb').write(b'\xff\xd8\xff\xe0' + b'first-evidence' * 100)"
curl -sS -X POST "$API/tasks/$TID/evidence" -H "X-Actor-Id: $TECH" \
  -F "idempotency_key=e2e-ev1" -F "expected_version=8" \
  -F "file=@/tmp/e2e-evidence-1.jpg;type=image/jpeg" | J

echo "[9] submit_completion v=8"
curl -sS -X POST "$API/tasks/$TID/complete" -H "X-Actor-Id: $TECH" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-cp1","expected_version":8,"completion_text":"已更换压缩机"}' | J

echo "[10] reject_completion v=9 (reporter)"
curl -sS -X POST "$API/tasks/$TID/reject-finish" -H "X-Actor-Id: $REPORTER" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-rj1","expected_version":9,"reason":"还需要清理冷凝器"}' | J

echo "[11] record_progress again v=10"
curl -sS -X POST "$API/tasks/$TID/progress" -H "X-Actor-Id: $TECH" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-rp2","expected_version":10,"note":"清理冷凝器"}' | J

# 第二次完工也必须上传新证据（reject 后任务回到 IN_PROGRESS，version=10）
echo "[11a] upload_evidence (T19 second completion)"
python3 -c "open('/tmp/e2e-evidence-2.jpg','wb').write(b'\xff\xd8\xff\xe0' + b'second-evidence' * 100)"
curl -sS -X POST "$API/tasks/$TID/evidence" -H "X-Actor-Id: $TECH" \
  -F "idempotency_key=e2e-ev2" -F "expected_version=11" \
  -F "file=@/tmp/e2e-evidence-2.jpg;type=image/jpeg" | J

echo "[12] submit_completion v=11"
curl -sS -X POST "$API/tasks/$TID/complete" -H "X-Actor-Id: $TECH" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-cp2","expected_version":11,"completion_text":"清理完成"}' | J

echo "[13] accept_completion v=12 (reporter)"
curl -sS -X POST "$API/tasks/$TID/accept-finish" -H "X-Actor-Id: $REPORTER" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"e2e-af1","expected_version":12}' | J

echo
echo "=== Final ==="
curl -sS "$API/tasks/$TID" -H "X-Actor-Id: $REPORTER" | python3 -c "
import sys, json
d = json.load(sys.stdin)
t = d['task']
print('status =', t['status'])
print('version =', t['version'])
print('events =', len(d['events']))
print('appointments =', [(a['status']) for a in d['appointments']])
print('evidence =', len(d['evidence']))
print('pins =', len(d['pins']))
print('asset_id =', t.get('asset_id'))
print('reporter_id =', t.get('reporter_id'))
print('assignee_id =', t.get('assignee_id'))
print('event_types =', [e['event_type'] for e in d['events']])
"