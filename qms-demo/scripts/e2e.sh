#!/usr/bin/env bash
set -euo pipefail
BASE="${1:-http://127.0.0.1:8088}"
TOKEN=$(curl -s -X POST "$BASE/api/auth/login" -d 'username=qc01&password=888888' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
AUTH="Authorization: Bearer $TOKEN"
PID=$(curl -s -H "$AUTH" "$BASE/api/projects" | python3 -c 'import sys,json;print(json.load(sys.stdin)[0]["id"])')
SID=$(curl -s -H "$AUTH" "$BASE/api/projects" | python3 -c 'import sys,json;print(json.load(sys.stdin)[0]["sections"][0]["id"])')
WBS=$(curl -s -H "$AUTH" "$BASE/api/wbs/tree?section_id=$SID" | python3 -c 'import sys,json;d=json.load(sys.stdin)
def walk(ns):
  for n in ns:
    yield n
    yield from walk(n.get("children") or [])
for n in walk(d):
  if n["code"]=="SG6-QL-01-01-001-01":
    print(n["id"]); break')
RESP=$(curl -s -H "$AUTH" -H 'Content-Type: application/json' -X POST "$BASE/api/forms/instances" -d "{\"template_code\":\"SB-43\",\"wbs_id\":\"$WBS\",\"data\":{\"project_name\":\"南天Demo\",\"contractor\":\"六标\",\"unit_name\":\"桥梁\",\"div_name\":\"下部\",\"component_name\":\"1#墩\",\"pour_date\":\"2026-07-01\",\"cure_method\":[\"覆盖\"],\"start_time\":\"2026-07-01 08:00\",\"recorder\":\"张工\",\"ambient_temp\":28}}")
IID=$(echo "$RESP" | python3 -c 'import sys,json;print(json.load(sys.stdin)["instance"]["id"])')
TID=$(echo "$RESP" | python3 -c 'import sys,json;print(json.load(sys.stdin)["task_id"])')
curl -s -H "$AUTH" -H 'Content-Type: application/json' -X PUT "$BASE/api/forms/instances/$IID" -d '{"data":{"project_name":"南天Demo","contractor":"六标","unit_name":"桥梁","div_name":"下部","component_name":"1#墩","pour_date":"2026-07-01","cure_method":["覆盖"],"start_time":"2026-07-01 08:00","recorder":"张工","ambient_temp":28},"submit":true}' >/dev/null
TOKEN2=$(curl -s -X POST "$BASE/api/auth/login" -d 'username=jl01&password=888888' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
curl -s -H "Authorization: Bearer $TOKEN2" -H 'Content-Type: application/json' -X POST "$BASE/api/tasks/$TID/action" -d '{"action":"approve","comment":"同意"}' | python3 -c 'import sys,json;d=json.load(sys.stdin);assert d["status"]=="approved", d; print("E2E OK", d["id"])'
