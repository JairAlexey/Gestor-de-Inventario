#!/usr/bin/env python3
"""
Script avanzado de DAST con OWASP ZAP.
Configura contexto, autenticación form-based y ejecuta spider + active scan.
"""
import os
import sys
import json
import time
from zapv2 import ZAPv2

# Configuración desde variables de entorno
TARGET_URL = os.getenv('DAST_TARGET_URL', 'https://gestor-de-inventario-production.up.railway.app')
LOGIN_URL = os.getenv('DAST_LOGIN_URL', f'{TARGET_URL}/login/')
USERNAME = os.getenv('DAST_LOGIN_USER', 'admin')
PASSWORD = os.getenv('DAST_LOGIN_PASS', 'admin')
REPORT_DIR = os.getenv('ZAP_REPORT_DIR', '/zap/wrk')
ZAP_API_KEY = os.getenv('ZAP_API_KEY', '')
ZAP_PORT = int(os.getenv('ZAP_PORT', '8080'))


class ZAPScanner:
    def __init__(self):
        self.zap = ZAPv2(apikey=ZAP_API_KEY,
                         proxies={'http': f'http://localhost:{ZAP_PORT}',
                                  'https': f'http://localhost:{ZAP_PORT}'})
        self.context_name = 'GestorInventario'
        self.user_name = 'admin_user'

    def wait_for_zap(self, timeout=120):
        """Espera a que ZAP esté listo."""
        print("⏳ Esperando a que ZAP inicie...")
        start = time.time()
        while time.time() - start < timeout:
            try:
                self.zap.core.version
                print("✅ ZAP está listo")
                return True
            except Exception:
                time.sleep(2)
        print("❌ Timeout esperando a ZAP")
        return False

    def create_context(self):
        """Crea un contexto para la aplicación."""
        print(f"📝 Creando contexto '{self.context_name}'...")

        # Crear contexto
        context_id = self.zap.context.new_context(self.context_name)
        print(f"   Context ID: {context_id}")

        # Incluir URL en el contexto
        self.zap.context.include_in_context(self.context_name, f'{TARGET_URL}.*')
        print(f"   ✅ URL incluida en contexto: {TARGET_URL}.*")

        # Excluir logout
        logout_regex = f'{TARGET_URL}/logout/.*'
        self.zap.context.exclude_from_context(self.context_name, logout_regex)
        print(f"   ✅ Excluido logout: {logout_regex}")

        return context_id

    def configure_authentication(self, context_id):
        """Configura autenticación form-based."""
        print("🔐 Configurando autenticación form-based...")

        # Configurar autenticación
        login_url = LOGIN_URL
        login_request_data = 'username={%username%}&password={%password%}&csrfmiddlewaretoken=ZAP'

        # Establecer método de autenticación
        self.zap.authentication.set_authentication_method(
            contextid=context_id,
            authmethodname='formBasedAuthentication',
            authmethodconfigparams=f'loginUrl={login_url}&loginRequestData={login_request_data}'
        )
        print("   ✅ Método configurado: Form-based")
        print(f"   Login URL: {login_url}")

        # Indicadores de sesión
        logged_in_indicator = 'Cerrar Sesión'
        logged_out_indicator = 'Iniciar Sesión'

        self.zap.authentication.set_logged_in_indicator(context_id, logged_in_indicator)
        self.zap.authentication.set_logged_out_indicator(context_id, logged_out_indicator)
        print(f"   ✅ Logged-in indicator: '{logged_in_indicator}'")
        print(f"   ✅ Logged-out indicator: '{logged_out_indicator}'")

    def create_user(self, context_id):
        """Crea un usuario para autenticación."""
        print(f"👤 Creando usuario '{self.user_name}'...")

        user_id = self.zap.users.new_user(context_id, self.user_name)
        print(f"   User ID: {user_id}")

        # Configurar credenciales
        auth_config = f'username={USERNAME}&password={PASSWORD}'
        self.zap.users.set_authentication_credentials(context_id, user_id, auth_config)
        print("   ✅ Credenciales configuradas")

        # Habilitar usuario
        self.zap.users.set_user_enabled(context_id, user_id, True)
        print("   ✅ Usuario habilitado")

        return user_id

    def spider_scan(self, user_id):
        """Ejecuta spider scan autenticado."""
        print("\n🕷️  Iniciando Spider Scan (autenticado)...")

        scan_id = self.zap.spider.scan_as_user(
            contextid=self.context_name,
            userid=user_id,
            url=TARGET_URL,
            recurse=True
        )
        print(f"   Scan ID: {scan_id}")

        # Esperar a que termine
        while int(self.zap.spider.status(scan_id)) < 100:
            progress = self.zap.spider.status(scan_id)
            print(f"   Progress: {progress}%", end='\r')
            time.sleep(2)

        print("\n   ✅ Spider completado")

        # Mostrar URLs encontradas
        urls = self.zap.spider.results(scan_id)
        print(f"   📊 URLs encontradas: {len(urls)}")
        return urls

    def active_scan(self, user_id):
        """Ejecuta active scan autenticado."""
        print("\n🔍 Iniciando Active Scan (autenticado)...")

        scan_id = self.zap.ascan.scan_as_user(
            url=TARGET_URL,
            contextid=self.context_name,
            userid=user_id,
            recurse=True
        )
        print(f"   Scan ID: {scan_id}")

        # Esperar a que termine
        while int(self.zap.ascan.status(scan_id)) < 100:
            progress = self.zap.ascan.status(scan_id)
            print(f"   Progress: {progress}%", end='\r')
            time.sleep(5)

        print("\n   ✅ Active scan completado")

    def generate_reports(self):
        """Genera reportes en múltiples formatos."""
        print("\n📄 Generando reportes...")

        os.makedirs(REPORT_DIR, exist_ok=True)

        # HTML Report
        html_report = self.zap.core.htmlreport()
        with open(f'{REPORT_DIR}/zap-report.html', 'w') as f:
            f.write(html_report)
        print(f"   ✅ HTML: {REPORT_DIR}/zap-report.html")

        # JSON Report
        json_report = self.zap.core.jsonreport()
        with open(f'{REPORT_DIR}/zap-report.json', 'w') as f:
            f.write(json_report)
        print(f"   ✅ JSON: {REPORT_DIR}/zap-report.json")

        # Markdown Report
        alerts = json.loads(json_report)
        self.generate_markdown_report(alerts)
        print(f"   ✅ Markdown: {REPORT_DIR}/zap-report.md")

        return json.loads(json_report)

    def generate_markdown_report(self, alerts_data):
        """Genera un reporte en formato Markdown."""
        with open(f'{REPORT_DIR}/zap-report.md', 'w') as f:
            f.write("# OWASP ZAP Security Report\n\n")
            f.write(f"**Target:** {TARGET_URL}\n\n")
            f.write(f"**Scan Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Contar alertas por riesgo
            risk_counts = {'High': 0, 'Medium': 0, 'Low': 0, 'Informational': 0}

            if 'site' in alerts_data:
                for site in alerts_data['site']:
                    if 'alerts' in site:
                        for alert in site['alerts']:
                            risk = alert.get('risk', 'Informational')
                            risk_counts[risk] = risk_counts.get(risk, 0) + 1

            f.write("## Summary\n\n")
            f.write(f"- 🔴 **High:** {risk_counts['High']}\n")
            f.write(f"- 🟠 **Medium:** {risk_counts['Medium']}\n")
            f.write(f"- 🟡 **Low:** {risk_counts['Low']}\n")
            f.write(f"- 🔵 **Informational:** {risk_counts['Informational']}\n\n")

            f.write("## Detailed Findings\n\n")
            if 'site' in alerts_data:
                for site in alerts_data['site']:
                    if 'alerts' in site:
                        for alert in site['alerts']:
                            f.write(f"### {alert.get('name', 'Unknown')}\n\n")
                            f.write(f"**Risk:** {alert.get('risk', 'N/A')}\n\n")
                            f.write(f"**Confidence:** {alert.get('confidence', 'N/A')}\n\n")
                            f.write(f"**Description:** {alert.get('desc', 'N/A')}\n\n")
                            if 'instances' in alert:
                                f.write(f"**Instances:** {len(alert['instances'])}\n\n")
                            f.write("---\n\n")

    def analyze_results(self, report_data):
        """Analiza los resultados y determina si el build debe fallar."""
        print("\n📊 Análisis de Resultados:")

        high_count = 0
        medium_count = 0
        low_count = 0

        if 'site' in report_data:
            for site in report_data['site']:
                if 'alerts' in site:
                    for alert in site['alerts']:
                        risk = alert.get('risk', '')
                        if risk == 'High':
                            high_count += 1
                        elif risk == 'Medium':
                            medium_count += 1
                        elif risk == 'Low':
                            low_count += 1

        print(f"   🔴 High: {high_count}")
        print(f"   🟠 Medium: {medium_count}")
        print(f"   🟡 Low: {low_count}")

        if high_count > 0:
            print(f"\n❌ FALLO: Se encontraron {high_count} alertas de riesgo ALTO")
            return False
        elif medium_count > 0:
            print(f"\n⚠️  ADVERTENCIA: Se encontraron {medium_count} alertas de riesgo MEDIO")
            # Puedes cambiar esto a False para fallar también con Medium
            return True
        else:
            print("\n✅ No se encontraron vulnerabilidades críticas")
            return True

    def run(self):
        """Ejecuta el escaneo completo."""
        try:
            if not self.wait_for_zap():
                return False

            print(f"\n{'='*60}")
            print(f"🎯 Target: {TARGET_URL}")
            print(f"👤 User: {USERNAME}")
            print(f"{'='*60}\n")

            context_id = self.create_context()
            self.configure_authentication(context_id)
            user_id = self.create_user(context_id)

            self.spider_scan(user_id)
            self.active_scan(user_id)

            report_data = self.generate_reports()
            success = self.analyze_results(report_data)

            print(f"\n{'='*60}")
            if success:
                print("✅ DAST completado exitosamente")
            else:
                print("❌ DAST completado con vulnerabilidades críticas")
            print(f"{'='*60}\n")

            return success

        except Exception as e:
            print(f"\n❌ Error durante el escaneo: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    scanner = ZAPScanner()
    success = scanner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
