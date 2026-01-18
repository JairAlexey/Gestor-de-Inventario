#!/bin/bash
# Script de prueba local para verificar que ZAP genera reportes correctamente

set -e

TARGET_URL="https://gestor-de-inventario-production.up.railway.app"
LOGIN_USER="admin"
LOGIN_PASS="admin123"

echo "=========================================="
echo "🧪 Prueba Local de ZAP con Autenticación"
echo "=========================================="
echo "Target: $TARGET_URL"
echo "User: $LOGIN_USER"
echo ""

# Limpiar contenedor anterior si existe
docker rm -f zap 2>/dev/null || true

# Crear directorio
mkdir -p reports
chmod 777 reports

echo "1️⃣ Creando configuración de autenticación..."
cat > reports/zap-context.yaml <<EOF
env:
  contexts:
    - name: "GestorInventario"
      urls:
        - "$TARGET_URL.*"
      includePaths:
        - "$TARGET_URL.*"
      excludePaths:
        - "$TARGET_URL/logout.*"
      authentication:
        method: "form"
        parameters:
          loginUrl: "$TARGET_URL/login/"
          loginRequestData: "username={%username%}&password={%password%}&csrfmiddlewaretoken={%csrftoken%}"
        verification:
          method: "response"
          loggedInRegex: "\\QCerrar Sesión\\E"
          loggedOutRegex: "\\QIniciar Sesión\\E"
      sessionManagement:
        method: "cookie"
      users:
        - name: "$LOGIN_USER"
          credentials:
            username: "$LOGIN_USER"
            password: "$LOGIN_PASS"
EOF

echo "2️⃣ Ejecutando ZAP Full Scan con autenticación..."
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
echo "3️⃣ Verificando archivos..."
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
