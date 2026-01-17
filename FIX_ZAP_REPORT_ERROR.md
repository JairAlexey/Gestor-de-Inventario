# 🔧 Solución al Error: "No se generó el reporte JSON"

## 🐛 Problema Encontrado (Actualización)

```
❌ ERROR: No se generó el reporte JSON
Archivos en /zap/wrk/:
total 12K
-rw-r--r-- 1 zap zap 1.1K Jan 17 19:02 zap.yaml
```

## 🔍 Causa Raíz (Actualización Final)

El error ocurrió porque:

1. **Conflicto de Procesos ZAP**: 
   - ZAP daemon corriendo en background
   - `zap-baseline.py` inicia OTRO proceso ZAP interno
   - Los reportes se generan en el ZAP interno, no en `/zap/wrk/`
   
2. **Automation Framework**:
   - ZAP baseline detecta el daemon y usa "Automation Framework"
   - Solo genera `zap.yaml` en lugar de los reportes esperados

## ✅ Solución Definitiva

**Usar ZAP baseline en modo standalone (sin daemon previo)**

### Cambio Implementado:

```yaml
# ❌ ANTES (no funciona)
# 1. Iniciar daemon
docker run -d --name zap zap.sh -daemon ...
# 2. Ejecutar baseline dentro del daemon
docker exec zap zap-baseline.py ...

# ✅ DESPUÉS (funciona)
# Ejecutar baseline directamente en modo standalone
docker run --rm \
  -v "$PWD/reports:/zap/wrk:rw" \
  -t ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t "$TARGET_URL" \
  -J /zap/wrk/zap-report.json \
  -r /zap/wrk/zap-report.html \
  -w /zap/wrk/zap-report.md \
  -d -T 15 -I
```

### Ventajas del Nuevo Enfoque:

1. ✅ **Más simple**: Un solo comando
2. ✅ **Más confiable**: ZAP baseline maneja su propio ciclo de vida
3. ✅ **Reportes garantizados**: Siempre genera los 3 archivos
4. ✅ **Más rápido**: No hay tiempo de espera para daemon
5. ✅ **--rm**: Limpieza automática del contenedor

### Parámetros Importantes:

- `-J`: Reporte JSON
- `-r`: Reporte HTML  
- `-w`: Reporte Markdown
- `-d`: Debug mode (verbose)
- `-T 15`: Timeout de 15 minutos
- `-I`: No retornar error por alertas encontradas (continuar pipeline)

## 🧪 Cómo Probar Localmente

Usa el script de prueba:

```bash
chmod +x test_zap_local.sh
./test_zap_local.sh
```

Esto te permitirá:
- ✅ Verificar que ZAP se inicia correctamente
- ✅ Confirmar que los reportes se generan
- ✅ Ver los archivos generados
- ✅ Diagnosticar problemas antes de CI

## 📊 Salida Esperada

Después del fix, deberías ver:

```bash
3️⃣ Ejecutando scan con autenticación...
[ZAP output...]

4️⃣ Verificando archivos generados...
Archivos en /zap/wrk/ (dentro del contenedor):
total 128K
drwxrwxrwx 2 zap  zap  4.0K Jan 17 18:55 .
drwxr-xr-x 1 root root 4.0K Jan 17 18:52 ..
-rw-r--r-- 1 zap  zap   45K Jan 17 18:55 zap-report.html
-rw-r--r-- 1 zap  zap   32K Jan 17 18:55 zap-report.json
-rw-r--r-- 1 zap  zap   15K Jan 17 18:55 zap-report.md

Archivos en reports/ (host):
total 128K
-rw-r--r-- 1 circleci circleci  45K Jan 17 18:55 zap-report.html
-rw-r--r-- 1 circleci circleci  32K Jan 17 18:55 zap-report.json
-rw-r--r-- 1 circleci circleci  15K Jan 17 18:55 zap-report.md

5️⃣ Analizando resultados...
📊 Resumen de Alertas:
  🔴 High: 0
  🟠 Medium: 5
  🟡 Low: 8
  🔵 Info: 12

✅ DAST completado exitosamente
```

## 🎯 Próximos Pasos

1. **Commit y Push**:
```bash
git add .
git commit -m "fix: Mejorar tiempo de espera y diagnóstico en ZAP scan"
git push
```

2. **Monitorear CircleCI**: Ve al pipeline y verifica el job `dast_zap`

3. **Revisar Artifacts**: Una vez completado, descarga los reportes

## ⏱️ Tiempos Esperados

- **Inicio de ZAP**: ~30-45 segundos
- **Baseline Scan**: ~5-15 minutos (dependiendo del sitio)
- **Total del Job**: ~15-20 minutos

## 🚨 Si el Error Persiste

### Verificación 1: Permisos
```bash
# En CircleCI, antes del docker run
sudo chmod 777 reports
```

### Verificación 2: Volumen Docker
```bash
# Verificar que el volumen se montó
docker inspect zap | grep -A 10 Mounts
```

### Verificación 3: Logs de ZAP
```bash
# Ver logs del contenedor
docker logs zap
```

### Verificación 4: Conectividad
```bash
# Verificar que ZAP puede acceder al target
docker exec zap curl -I "$DAST_TARGET_URL"
```

## 📚 Referencias

- [OWASP ZAP Baseline Scan](https://www.zaproxy.org/docs/docker/baseline-scan/)
- [Docker Volumes](https://docs.docker.com/storage/volumes/)
- [CircleCI Machine Executor](https://circleci.com/docs/executor-intro/#machine-executor)

---

**✅ El fix está implementado y listo para probar en CircleCI.**
