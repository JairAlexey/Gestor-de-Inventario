#!/bin/bash
# Script de prueba local para verificar que ZAP genera reportes correctamente

set -e

TARGET_URL="https://gestor-de-inventario-production.up.railway.app"

echo "=========================================="
echo "🧪 Prueba Local de ZAP Full Scan"
echo "=========================================="
echo "Target: $TARGET_URL"
echo ""

# Limpiar contenedor anterior si existe
docker rm -f zap 2>/dev/null || true

# Crear directorio
mkdir -p reports
chmod 777 reports

echo "1️⃣ Ejecutando ZAP Full Scan..."
docker run --rm \
  -v "$PWD/reports:/zap/wrk:rw" \
  -t ghcr.io/zaproxy/zaproxy:stable \
  zap-full-scan.py \
  -t "$TARGET_URL" \
  -J zap-report.json \
  -r zap-report.html \
  -w zap-report.md \
  -d \
  -T 10 \
  -m 5 \
  || echo "⚠️  Scan completado con warnings"

echo ""
echo "2️⃣ Verificando archivos..."
ls -lah reports/

if [ -f "reports/zap-report.json" ]; then
  echo ""
  echo "✅ ÉXITO: Reporte generado"
  echo "Tamaño: $(ls -lh reports/zap-report.json | awk '{print $5}')"
else
  echo ""
  echo "❌ FALLO: No se generó el reporte"
  exit 1
fi
