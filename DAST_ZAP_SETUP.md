# 🕷️ OWASP ZAP - Implementación Completada

## ✅ Cambios Realizados

### 1. Archivos Creados

#### `security/zap/`
- **`README.md`** - Documentación completa del sistema DAST
- **`zap_authenticated_scan.py`** - Script Python con ZAP API para autenticación form-based
- **`zap_auth_selenium.py`** - Script Selenium para login con manejo de CSRF
- **`zap_scan.sh`** - Script bash simple para baseline scan
- **`zap_advanced_scan.sh`** - Script bash avanzado con Selenium + ZAP
- **`requirements.txt`** - Dependencias Python para scripts

### 2. CircleCI Actualizado

#### Cambios en `.circleci/config.yml`:
- ❌ **Eliminado**: Job `dast_arachni`
- ✅ **Agregado**: Job `dast_zap` con:
  - Machine executor (ubuntu-2204:current) para Docker
  - Variables de entorno configuradas
  - Verificación de conectividad
  - ZAP daemon en contenedor
  - Baseline scan con reportes HTML/JSON/MD
  - Análisis de vulnerabilidades
  - Fallo automático si hay alertas HIGH
  - Store artifacts para reportes

## 🔧 Configuración Requerida en CircleCI

### Variables de Entorno

Configura estas variables en **CircleCI Project Settings > Environment Variables**:

```
DAST_TARGET_URL=https://gestor-de-inventario-production.up.railway.app
DAST_LOGIN_USER=admin
DAST_LOGIN_PASS=admin
DAST_LOGIN_PATH=/login/
```

### Pasos para Configurar:

1. Ve a https://app.circleci.com/
2. Selecciona tu proyecto "Gestor-de-Inventario"
3. Click en **Project Settings** ⚙️
4. En el menú lateral: **Environment Variables**
5. Click **Add Environment Variable**
6. Agrega cada variable (sin comillas en los valores)

**Nota**: Si no configuras las variables, usará los valores por defecto del YAML.

## 📊 Funcionamiento del Pipeline

### Workflow Actualizado:

```
build
  ↓
lint_test_and_coverage
  ↓
sast_sonarqube
  ↓
smoke_test
  ↓
dast_zap  ← NUEVO (reemplaza dast_arachni)
  ↓
build_and_push_image
```

### Proceso del Job `dast_zap`:

1. **Checkout** del código
2. **Verificación** de conectividad con Railway (curl)
3. **Inicio** de ZAP daemon en Docker
4. **Baseline Scan**:
   - Spider para descubrir URLs
   - Passive scanning
   - Análisis de seguridad
5. **Generación** de reportes:
   - `reports/zap-report.html` (visual)
   - `reports/zap-report.json` (datos)
   - `reports/zap-report.md` (resumen)
6. **Análisis** de vulnerabilidades por severidad
7. **Fallo** si hay alertas HIGH
8. **Upload** de artifacts a CircleCI

## 🔐 Autenticación

### Implementación Actual (Simple):

El job usa **ZAP baseline scan** sin autenticación completa. Esto funciona para:
- ✅ Escaneo de páginas públicas
- ✅ Detección de vulnerabilidades en login
- ✅ Análisis de headers de seguridad
- ⚠️ Limitado en páginas protegidas

### Por Qué Este Enfoque:

1. **Simplicidad**: No requiere configuración compleja en CI
2. **Confiabilidad**: Menor probabilidad de fallos por problemas de auth
3. **Velocidad**: Baseline scan es más rápido (5-10 min vs 20-30 min)
4. **Suficiente para empezar**: Detecta la mayoría de vulnerabilidades comunes

### Autenticación Completa (Opcional - Scripts Disponibles):

Si necesitas escanear rutas protegidas, tienes 2 opciones:

#### Opción A: Selenium (Más Robusto)
Script: `security/zap/zap_auth_selenium.py`
- Usa Selenium WebDriver para hacer login real
- Maneja CSRF tokens de Django automáticamente
- Exporta cookies de sesión
- Requiere: Chrome/Chromium en el contenedor

#### Opción B: ZAP API Form-Based
Script: `security/zap/zap_authenticated_scan.py`
- Configura contexto y usuario en ZAP
- Autenticación form-based con indicadores logged-in/out
- Spider y Active Scan autenticados
- Requiere: Configurar CSRF y verificar indicadores

**Para implementar autenticación completa**, necesitarías:
1. Modificar el job en CircleCI para usar uno de estos scripts
2. Instalar dependencias adicionales (Selenium/Chrome o python-owasp-zap-v2.4)
3. Aumentar el timeout del job (de 15 min a 30 min)

## 🚨 Criterios de Fallo

El build falla si:
- ✅ Se encuentran **1 o más alertas HIGH**
- ✅ No se puede generar el reporte JSON
- ✅ La aplicación Railway no es accesible

Para fallar también con alertas MEDIUM:

```yaml
# En .circleci/config.yml, línea ~130, cambiar:
if [ "$HIGH" -gt 0 ]; then

# Por:
if [ "$HIGH" -gt 0 ] || [ "$MEDIUM" -gt 0 ]; then
```

## 📄 Verificación de Resultados

### En CircleCI:

1. Ve a tu pipeline
2. Click en el job `dast_zap`
3. En la pestaña **Artifacts**:
   - Descarga `zap-reports/zap-report.html`
   - Abre en navegador para ver reporte visual

### Verificar Autenticación Exitosa:

En el reporte HTML, busca:
- ✅ **"Sites"** > Ver si hay URLs como `/dashboard/`, `/productos/`
- ✅ **"Alerts"** > Verificar que no todas sean en `/login/`
- ✅ Más de 20-30 URLs escaneadas

Indicadores de problemas:
- ❌ Solo 5-10 URLs
- ❌ Todas las URLs apuntan a `/login/`
- ❌ Solo alertas en página de login

## 🎯 Próximos Pasos

### Inmediato:
1. ✅ Hacer commit y push de estos cambios
2. ✅ Configurar variables en CircleCI
3. ✅ Ejecutar pipeline y verificar el job `dast_zap`
4. ✅ Revisar los artifacts/reportes

### Corto Plazo:
1. Revisar y resolver alertas HIGH si aparecen
2. Considerar implementar autenticación completa si necesitas escanear rutas protegidas
3. Ajustar el criterio de fallo (incluir MEDIUM si es necesario)

### Largo Plazo:
1. Crear un ambiente de **staging en Railway** para DAST (recomendado)
2. Configurar **rate limiting** en Django para proteger de scans agresivos
3. Implementar **ZAP full scan** mensualmente (más exhaustivo)
4. Integrar reportes de ZAP con **Defect Dojo** o similar

## 🔗 Ambiente de Staging (Recomendado)

**¿Por qué?**
- No impactas producción con scans agresivos
- Puedes tener un usuario de testing específico
- Datos de prueba en vez de datos reales

**Cómo implementar:**
1. En Railway, crea un nuevo servicio desde el mismo repo
2. Usa una branch diferente (ej: `staging`)
3. Configura variables de entorno de staging
4. Actualiza `DAST_TARGET_URL` en CircleCI para apuntar a staging

## 📚 Recursos

- [OWASP ZAP Docs](https://www.zaproxy.org/docs/)
- [ZAP Baseline Scan](https://www.zaproxy.org/docs/docker/baseline-scan/)
- [Django Security Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)
- Scripts adicionales en: `security/zap/README.md`

## ⚠️ Consideraciones Importantes

### Producción:
- El scan se ejecuta contra **Railway producción**
- Puede generar logs y alertas en tu app
- No afectará el funcionamiento pero incrementará el tráfico

### Performance:
- El scan toma **5-15 minutos**
- Usa timeout de 15 min configurado en ZAP
- Si necesitas más tiempo, ajusta `-T 15` a `-T 30`

### False Positives:
- ZAP puede reportar **falsos positivos**
- Siempre revisa manualmente las alertas HIGH
- Usa el contexto de tu aplicación para validar

### CSRF:
- Django usa tokens CSRF dinámicos
- ZAP baseline puede tener problemas con forms protegidos
- Para escaneo completo de forms, usa Selenium

## 🆘 Troubleshooting

### Error: "No se pudo conectar a TARGET_URL"
- Verifica que Railway esté en línea
- Revisa la URL en las variables de entorno
- Confirma que no hay firewall bloqueando CircleCI

### Error: "No se generó el reporte JSON"
- Verifica los logs de ZAP en el output del job
- Puede ser timeout - aumenta `-T` en el comando
- Verifica permisos del directorio `reports/`

### Pocas URLs encontradas (< 10)
- La autenticación no funcionó
- Considera implementar Selenium
- Verifica que el usuario admin/admin existe y funciona

### Job toma demasiado tiempo
- Reduce el timeout: `-T 15` a `-T 10`
- Usa baseline en vez de full scan
- Limita el scope con `-I` (include) y `-X` (exclude)

## 📞 Soporte

Si necesitas ayuda con:
- Implementar autenticación completa
- Configurar staging environment
- Resolver alertas específicas de ZAP
- Optimizar el scan

Revisa la documentación en `security/zap/README.md` o consulta los scripts de ejemplo.

---

**Versión**: 1.0
**Fecha**: 2026-01-17
**Estado**: ✅ Listo para producción
