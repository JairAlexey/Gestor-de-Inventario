#!/bin/bash
# Script de prueba local para verificar que ZAP genera reportes correctamente

set -e

TARGET_URL="https://gestor-de-inventario-production.up.railway.app"

echo "=========================================="
echo "🧪 Prueba Local de ZAP"
echo "=========================================="
echo "Target: $TARGET_URL"
echo ""

# Limpiar contenedor anterior si existe
docker rm -f zap 2>/dev/null || true

# Crear directorio
mkdir -p reports
chmod 777 reports

echo "1️⃣ Iniciando ZAP..."
docker run -d --name zap \
  -u zap \
  -p 8080:8080 \
  -v "$PWD/reports:/zap/wrk:rw" \
  ghcr.io/zaproxy/zaproxy:stable \
  zap.sh -daemon -host 0.0.0.0 -port 8080 \
  -config api.addrs.addr.name=.* \
  -config api.addrs.addr.regex=true \
  -config api.disablekey=true

echo "⏳ Esperando 30s..."
sleep 30

echo ""
echo "2️⃣ Verificando ZAP API..."
for i in {1..5}; do
  if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ ZAP API respondiendo"
    break
  fi
  echo "Intento $i/5..."
  sleep 5
done

echo ""
echo "3️⃣ Ejecutando baseline scan..."
docker exec zap \
  zap-baseline.py \
  -t "$TARGET_URL" \
  -J /zap/wrk/zap-report.json \
  -r /zap/wrk/zap-report.html \
  -w /zap/wrk/zap-report.md \
  -d \
  -T 5 \
  || echo "⚠️  Scan completado con warnings"

echo ""
echo "4️⃣ Verificando archivos..."
echo "En contenedor:"
docker exec zap ls -lah /zap/wrk/

echo ""
echo "En host:"
ls -lah reports/

echo ""
echo "5️⃣ Limpiando..."
docker stop zap
docker rm zap

if [ -f "reports/zap-report.json" ]; then
  echo ""
  echo "✅ ÉXITO: Reporte generado"
  echo "Tamaño: $(ls -lh reports/zap-report.json | awk '{print $5}')"
else
  echo ""
  echo "❌ FALLO: No se generó el reporte"
  exit 1
fi
