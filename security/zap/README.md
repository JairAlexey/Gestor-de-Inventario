# OWASP ZAP - Security Testing

Este directorio contiene scripts y configuraciones para ejecutar pruebas de seguridad DAST (Dynamic Application Security Testing) con OWASP ZAP.

## 📁 Archivos

- **`zap_authenticated_scan.py`**: Script Python avanzado que usa la API de ZAP para configurar autenticación form-based y ejecutar spider + active scan
- **`zap_auth_selenium.py`**: Script alternativo que usa Selenium para realizar login y exportar cookies
- **`zap_scan.sh`**: Script bash para ejecutar ZAP baseline scan

## 🔧 Configuración en CircleCI

### Variables de Entorno Requeridas

Configura estas variables en tu proyecto de CircleCI (Settings > Environment Variables):

| Variable | Descripción | Valor por Defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `DAST_TARGET_URL` | URL de la aplicación en Railway | `https://gestor-de-inventario-production.up.railway.app` | ✅ |
| `DAST_LOGIN_USER` | Usuario para autenticación | `admin` | ✅ |
| `DAST_LOGIN_PASS` | Contraseña del usuario | `admin` | ✅ |
| `DAST_LOGIN_PATH` | Ruta del formulario de login | `/login/` | ❌ |

### Cómo Configurar Variables en CircleCI

1. Ve a tu proyecto en CircleCI
2. Click en **Project Settings** (⚙️)
3. Selecciona **Environment Variables** en el menú lateral
4. Click en **Add Environment Variable**
5. Agrega cada variable con su valor correspondiente

**Importante**: No uses comillas en los valores de las variables.

## 🕷️ Funcionamiento del DAST

El job `dast_zap` en CircleCI ejecuta los siguientes pasos:

1. **Verificación de Conectividad**: Hace un curl a Railway para confirmar que la app está accesible
2. **Inicio de ZAP**: Lanza ZAP daemon en un contenedor Docker
3. **Baseline Scan**: Ejecuta ZAP baseline scan que incluye:
   - Spider para descubrir URLs
   - Passive scanning de vulnerabilidades
   - Análisis de seguridad básico
4. **Generación de Reportes**: Crea 3 reportes:
   - `zap-report.html` - Reporte visual interactivo
   - `zap-report.json` - Datos estructurados para análisis
   - `zap-report.md` - Resumen en Markdown
5. **Análisis de Resultados**: Cuenta alertas por severidad y falla el build si hay alertas HIGH

## 🔐 Verificar Autenticación Exitosa

Para verificar que ZAP logró autenticarse correctamente:

### En el Reporte HTML (`zap-report.html`):

1. Busca la sección **"Sites"** o **"URLs"**
2. Verifica que aparezcan URLs protegidas como:
   - `/dashboard/`
   - `/productos/`
   - `/categorias/`
3. Busca que NO haya múltiples redirecciones a `/login/`

### En el Reporte JSON (`zap-report.json`):

```bash
# Ver todas las URLs escaneadas
cat reports/zap-report.json | grep -o '"url":"[^"]*"' | sort -u

# Verificar que no todo sea redireccionado a login
cat reports/zap-report.json | grep -c "login" 
cat reports/zap-report.json | grep -c "dashboard"
```

### Indicadores de Autenticación Exitosa:

✅ **Bueno**:
- Más de 20-30 URLs encontradas
- URLs como `/dashboard/`, `/productos/lista/`, etc.
- Alertas en páginas protegidas (no solo en `/login/`)

❌ **Problema**:
- Solo 5-10 URLs encontradas
- Todas las URLs apuntan a `/login/`
- Alertas solo en página de login

## 🚨 Criterios de Fallo del Build

El job falla si:
- ✅ Se encuentran alertas de riesgo **HIGH** (Alto)
- ⚠️ Alertas **MEDIUM** generan warning pero no fallan (modificable)
- ✅ No se pueden generar los reportes
- ✅ La aplicación no es accesible

Para hacer que también falle con alertas MEDIUM, modifica en `.circleci/config.yml`:

```bash
# Cambiar:
if [ "$HIGH" -gt 0 ]; then

# Por:
if [ "$HIGH" -gt 0 ] || [ "$MEDIUM" -gt 0 ]; then
```

## 📊 Interpretación de Resultados

### Niveles de Riesgo

| Nivel | Emoji | Descripción | Acción |
|-------|-------|-------------|--------|
| **High** | 🔴 | Vulnerabilidad crítica | ❌ Falla el build |
| **Medium** | 🟠 | Vulnerabilidad importante | ⚠️ Revisar |
| **Low** | 🟡 | Vulnerabilidad menor | ℹ️ Informativo |
| **Informational** | 🔵 | No es vulnerabilidad | ℹ️ Informativo |

### Vulnerabilidades Comunes en Django

- **Missing Anti-CSRF Tokens**: Verifica que todos los forms tengan `{% csrf_token %}`
- **X-Frame-Options Header Not Set**: Configura `X_FRAME_OPTIONS = 'DENY'` en settings
- **X-Content-Type-Options Header Missing**: Django lo incluye por defecto en producción
- **Cookie No HttpOnly Flag**: Revisa `SESSION_COOKIE_HTTPONLY = True`
- **Cookie Without Secure Flag**: Para HTTPS: `SESSION_COOKIE_SECURE = True`

## 🔧 Ejecución Local (Opcional)

Si quieres ejecutar ZAP localmente:

```bash
# 1. Iniciar ZAP daemon
docker run -d --name zap \
  -u zap \
  -p 8080:8080 \
  -v $(pwd)/reports:/zap/wrk:rw \
  ghcr.io/zaproxy/zaproxy:stable \
  zap.sh -daemon -host 0.0.0.0 -port 8080 \
  -config api.disablekey=true

# 2. Ejecutar baseline scan
docker exec zap \
  zap-baseline.py \
  -t https://gestor-de-inventario-production.up.railway.app \
  -J /zap/wrk/zap-report.json \
  -r /zap/wrk/zap-report.html \
  -w /zap/wrk/zap-report.md

# 3. Ver reportes
ls -lh reports/

# 4. Limpiar
docker stop zap && docker rm zap
```

## 🎯 Mejores Prácticas

1. **No ejecutes DAST en producción**: Usa un ambiente de staging/testing
2. **Usuario de pruebas**: Crea un usuario específico para testing, no uses cuentas reales
3. **Rate limiting**: Configura rate limiting en tu app para protegerla de scans agresivos
4. **Baseline primero**: Empieza con baseline scan, luego considera full scan si necesitas más profundidad
5. **Revisa regularmente**: Ejecuta DAST en cada release o al menos semanalmente

## 📚 Referencias

- [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)
- [ZAP Baseline Scan](https://www.zaproxy.org/docs/docker/baseline-scan/)
- [ZAP Authentication](https://www.zaproxy.org/docs/authentication/)
- [Django Security](https://docs.djangoproject.com/en/5.1/topics/security/)

## ⚠️ Notas Importantes

- **Railway Production**: El scan se ejecuta contra producción. Considera crear un ambiente de staging
- **Performance**: El scan puede tomar 5-15 minutos dependiendo del tamaño de la app
- **False Positives**: ZAP puede reportar falsos positivos, revisa manualmente las alertas HIGH
- **CSRF**: Django usa CSRF tokens dinámicos que pueden complicar la autenticación automática
