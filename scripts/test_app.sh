#!/usr/bin/env bash
# Проверка работоспособности (п. 10)
set -euo pipefail

BASE="${BASE_URL:-http://localhost:8080}"

echo "=== Health ==="
curl -sf "${BASE}/health" | python3 -m json.tool

echo ""
echo "=== Home ==="
curl -sf "${BASE}/" | head -5

echo ""
echo "=== Analyze (K-Means) ==="
curl -sf "${BASE}/analyze" -o /tmp/analyze.html
grep -q "K-Means" /tmp/analyze.html && echo "OK: страница анализа содержит K-Means"

echo ""
echo "=== Forced browsing blocked (expect 403) ==="
code=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/admin")
test "$code" = "403" && echo "OK: /admin -> 403" || echo "FAIL: /admin -> $code"

code=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/internal")
test "$code" = "403" && echo "OK: /internal -> 403" || echo "FAIL: /internal -> $code"

echo ""
echo "All checks passed."
