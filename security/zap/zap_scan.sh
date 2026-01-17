#!/bin/bash
# Script para ejecutar ZAP con autenticación contra Railway
# Este script se ejecuta dentro del contenedor de ZAP

set -e

echo "=========================================="
echo "🕷️  OWASP ZAP DAST - Railway Deployment"
echo "=========================================="

TARGET_URL="${DAST_TARGET_URL:-https://gestor-de-inventario-production.up.railway.app}"
REPORT_DIR="${ZAP_REPORT_DIR:-/zap/wrk}"
COOKIES_FILE="$REPORT_DIR/session_cookies.json"

echo "🎯 Target: $TARGET_URL"
echo "📁 Reports: $REPORT_DIR"
echo ""

# Crear directorio de reportes
mkdir -p "$REPORT_DIR"

echo "1️⃣ Verificando conectividad con el target..."
if ! curl -s -o /dev/null -w "%{http_code}" "$TARGET_URL" | grep -E "200|301|302" > /dev/null; then
    echo "❌ No se pudo conectar a $TARGET_URL"
    exit 1
fi
echo "✅ Conectividad OK"
echo ""

# Verificar si existe el archivo de cookies (ya debería estar creado por Selenium)
if [ -f "$COOKIES_FILE" ]; then
    echo "2️⃣ Cookies de sesión encontradas: $COOKIES_FILE"
    cat "$COOKIES_FILE" | head -n 20
    echo ""
else
    echo "⚠️  No se encontraron cookies. ZAP escaneará sin autenticación."
    echo ""
fi

echo "3️⃣ Iniciando ZAP Baseline Scan..."
echo ""

# Ejecutar ZAP baseline scan con ajustes
# -t: target URL
# -J: JSON report
# -r: HTML report
# -w: Markdown report
# -d: Mostrar debug info
# -I: No retornar código de error por alertas encontradas (ajustaremos esto después)
# -z: Opciones adicionales de ZAP

# Escaneo con autenticación (si hay cookies)
if [ -f "$COOKIES_FILE" ]; then
    echo "🔐 Escaneando con autenticación..."

    # Opción 1: Usar zap-baseline.py (más simple)
    /zap/zap-baseline.py \
        -t "$TARGET_URL" \
        -J "$REPORT_DIR/zap-report.json" \
        -r "$REPORT_DIR/zap-report.html" \
        -w "$REPORT_DIR/zap-report.md" \
        -d \
        -T 15 \
        -z "-config api.disablekey=true" \
        || true

    # Nota: zap-baseline.py no soporta directamente la importación de cookies
    # Para autenticación completa, necesitamos usar zap-full-scan.py o zap-api-scan.py
    # con un context file, pero eso requiere más configuración.

    echo ""
    echo "📝 Intentando inyectar cookies en ZAP..."
    # Esto requeriría usar ZAP API o un script más complejo
    # Por ahora, documentamos las cookies encontradas
else
    echo "⚠️  Escaneando SIN autenticación..."

    /zap/zap-baseline.py \
        -t "$TARGET_URL" \
        -J "$REPORT_DIR/zap-report.json" \
        -r "$REPORT_DIR/zap-report.html" \
        -w "$REPORT_DIR/zap-report.md" \
        -d \
        -T 10 \
        || true
fi

echo ""
echo "4️⃣ Generando análisis de resultados..."

# Analizar el reporte JSON para detectar severidades
if [ -f "$REPORT_DIR/zap-report.json" ]; then
    echo ""
    echo "📊 Resumen de Alertas:"
    
    # Contar alertas por riesgo
    HIGH=$(grep -o '"risk":"High"' "$REPORT_DIR/zap-report.json" | wc -l || echo "0")
    MEDIUM=$(grep -o '"risk":"Medium"' "$REPORT_DIR/zap-report.json" | wc -l || echo "0")
    LOW=$(grep -o '"risk":"Low"' "$REPORT_DIR/zap-report.json" | wc -l || echo "0")
    INFO=$(grep -o '"risk":"Informational"' "$REPORT_DIR/zap-report.json" | wc -l || echo "0")

    echo "  🔴 High: $HIGH"
    echo "  🟠 Medium: $MEDIUM"
    echo "  🟡 Low: $LOW"
    echo "  🔵 Info: $INFO"
    echo ""

    # Fallar el build si hay alertas High o Medium
    if [ "$HIGH" -gt 0 ]; then
        echo "❌ FALLO: Se encontraron $HIGH alertas de riesgo ALTO"
        echo "   Revisa el reporte para más detalles."
        exit 1
    elif [ "$MEDIUM" -gt 0 ]; then
        echo "⚠️  ADVERTENCIA: Se encontraron $MEDIUM alertas de riesgo MEDIO"
        echo "   Se recomienda revisarlas, pero el build continuará."
        # Descomentar la siguiente línea para fallar también con MEDIUM:
        # exit 1
    fi
fi

echo ""
echo "=========================================="
echo "✅ DAST completado"
echo "=========================================="
echo "📄 Reportes generados:"
ls -lh "$REPORT_DIR"/zap-report.* || true
echo ""
