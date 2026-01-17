#!/bin/bash
# Script wrapper para ejecutar ZAP con autenticación avanzada usando Selenium + ZAP API
# Uso: ./zap_advanced_scan.sh

set -e

echo "=========================================="
echo "🕷️  OWASP ZAP Advanced Authenticated Scan"
echo "=========================================="

# Variables
TARGET_URL="${DAST_TARGET_URL:-https://gestor-de-inventario-production.up.railway.app}"
ZAP_PORT=8080
REPORT_DIR="${PWD}/reports"

echo "🎯 Target: $TARGET_URL"
echo "📁 Reports: $REPORT_DIR"
echo ""

# Crear directorio de reportes
mkdir -p "$REPORT_DIR"

# 1. Iniciar ZAP daemon
echo "1️⃣ Iniciando ZAP daemon..."
docker run -d --name zap \
  -u zap \
  -p ${ZAP_PORT}:${ZAP_PORT} \
  -v "${REPORT_DIR}:/zap/wrk:rw" \
  -v "${PWD}/security/zap:/zap/scripts:ro" \
  ghcr.io/zaproxy/zaproxy:stable \
  zap.sh -daemon -host 0.0.0.0 -port ${ZAP_PORT} \
  -config api.addrs.addr.name=.* \
  -config api.addrs.addr.regex=true \
  -config api.disablekey=true

echo "⏳ Esperando a que ZAP inicie (30s)..."
sleep 30

# Verificar que ZAP está corriendo
if ! docker ps | grep -q zap; then
    echo "❌ ERROR: ZAP no está corriendo"
    exit 1
fi

# 2. Opción A: Autenticación con Selenium (más robusta para CSRF)
echo ""
echo "2️⃣ Ejecutando autenticación con Selenium..."

# Instalar dependencias de Python en el contenedor
docker exec zap bash -c "
    pip install selenium requests || true
"

# Ejecutar script de autenticación
docker exec -e DAST_TARGET_URL="$TARGET_URL" \
  -e DAST_LOGIN_USER="${DAST_LOGIN_USER:-admin}" \
  -e DAST_LOGIN_PASS="${DAST_LOGIN_PASS:-admin}" \
  -e DAST_LOGIN_PATH="${DAST_LOGIN_PATH:-/login/}" \
  -e ZAP_COOKIES_FILE="/zap/wrk/session_cookies.json" \
  zap python3 /zap/scripts/zap_auth_selenium.py || {
    echo "⚠️  Autenticación con Selenium falló, continuando sin auth..."
}

# 3. Ejecutar spider y scan
echo ""
echo "3️⃣ Ejecutando spider scan..."

docker exec zap zap-cli quick-scan --self-contained \
  --spider \
  --ajax-spider \
  -r "$TARGET_URL" || true

echo ""
echo "4️⃣ Ejecutando active scan..."

docker exec zap zap-cli active-scan \
  --recursive \
  "$TARGET_URL" || true

# 5. Generar reportes
echo ""
echo "5️⃣ Generando reportes..."

docker exec zap zap-cli report -o /zap/wrk/zap-report.html -f html
docker exec zap zap-cli report -o /zap/wrk/zap-report.json -f json
docker exec zap zap-cli report -o /zap/wrk/zap-report.xml -f xml

# Generar también markdown
docker exec zap bash -c "
cat > /zap/wrk/zap-report.md <<'MDEOF'
# OWASP ZAP Security Scan Report

**Target:** $TARGET_URL
**Date:** $(date)

## Scan Summary

\$(zap-cli alerts -f json | python3 -c \"
import sys, json
try:
    data = json.load(sys.stdin)
    risks = {'High': 0, 'Medium': 0, 'Low': 0, 'Informational': 0}
    for alert in data:
        risk = alert.get('risk', 'Informational')
        risks[risk] = risks.get(risk, 0) + 1
    print(f'- 🔴 **High:** {risks[\"High\"]}')
    print(f'- 🟠 **Medium:** {risks[\"Medium\"]}')
    print(f'- 🟡 **Low:** {risks[\"Low\"]}')
    print(f'- 🔵 **Informational:** {risks[\"Informational\"]}')
except:
    print('Error parsing alerts')
\")

## Detailed Findings

\$(zap-cli alerts)

MDEOF
" || echo "⚠️  No se pudo generar reporte Markdown"

# 6. Análisis de resultados
echo ""
echo "6️⃣ Analizando resultados..."

if [ -f "$REPORT_DIR/zap-report.json" ]; then
    HIGH=$(grep -o '"risk":"High"' "$REPORT_DIR/zap-report.json" | wc -l || echo "0")
    MEDIUM=$(grep -o '"risk":"Medium"' "$REPORT_DIR/zap-report.json" | wc -l || echo "0")
    LOW=$(grep -o '"risk":"Low"' "$REPORT_DIR/zap-report.json" | wc -l || echo "0")

    echo "📊 Resumen:"
    echo "  🔴 High: $HIGH"
    echo "  🟠 Medium: $MEDIUM"
    echo "  🟡 Low: $LOW"

    # Verificar autenticación
    URLS_FOUND=$(grep -o '"url":"[^"]*"' "$REPORT_DIR/zap-report.json" | wc -l || echo "0")
    echo "  📄 URLs encontradas: $URLS_FOUND"

    if [ "$URLS_FOUND" -lt 10 ]; then
        echo "  ⚠️  Pocas URLs encontradas - la autenticación pudo haber fallado"
    fi

    # Detener ZAP
    echo ""
    echo "7️⃣ Deteniendo ZAP..."
    docker stop zap
    docker rm zap

    # Fallar si hay HIGH
    if [ "$HIGH" -gt 0 ]; then
        echo ""
        echo "❌ FALLO: Se encontraron $HIGH alertas de riesgo ALTO"
        exit 1
    fi

    echo ""
    echo "✅ Scan completado exitosamente"
else
    echo "❌ ERROR: No se generó el reporte JSON"
    docker stop zap
    docker rm zap
    exit 1
fi

echo "=========================================="
echo "📄 Reportes disponibles en: $REPORT_DIR"
ls -lh "$REPORT_DIR"/zap-report.* || true
echo "=========================================="
