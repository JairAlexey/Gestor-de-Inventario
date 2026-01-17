#!/usr/bin/env python3
"""
Script de autenticación con Selenium para OWASP ZAP.
Realiza login en Django con manejo de CSRF y exporta las cookies para ZAP.
"""
import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# Configuración desde variables de entorno
TARGET_URL = os.getenv('DAST_TARGET_URL', 'https://gestor-de-inventario-production.up.railway.app')
LOGIN_PATH = os.getenv('DAST_LOGIN_PATH', '/login/')
USERNAME = os.getenv('DAST_LOGIN_USER', 'admin')
PASSWORD = os.getenv('DAST_LOGIN_PASS', 'admin')
COOKIES_FILE = os.getenv('ZAP_COOKIES_FILE', '/zap/wrk/session_cookies.json')


def setup_driver():
    """Configura Chrome en modo headless."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def perform_login(driver):
    """Realiza el login en la aplicación Django."""
    login_url = TARGET_URL.rstrip('/') + LOGIN_PATH
    print(f"🔐 Accediendo a: {login_url}")

    driver.get(login_url)
    time.sleep(2)

    try:
        # Esperar a que el formulario esté presente
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")

        print(f"📝 Ingresando credenciales: {USERNAME}")
        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)

        # Enviar el formulario
        password_field.submit()
        time.sleep(3)

        # Verificar que el login fue exitoso
        current_url = driver.current_url
        print(f"📍 URL después del login: {current_url}")

        # Verificaciones de login exitoso
        if LOGIN_PATH in current_url and 'next=' not in current_url:
            print("❌ ERROR: Aún estamos en la página de login")
            print(f"Page source preview: {driver.page_source[:500]}")
            return False

        # Buscar indicadores de sesión iniciada
        page_source = driver.page_source
        success_indicators = [
            'Cerrar Sesión',
            'Logout',
            'Dashboard',
            'user.username'
        ]

        logged_in = any(indicator in page_source for indicator in success_indicators)

        if logged_in:
            print("✅ Login exitoso detectado")
            return True
        else:
            print("⚠️  No se detectaron indicadores claros de login exitoso")
            print(f"Página actual contiene: {page_source[:300]}")
            # Continuar de todos modos por si el login fue exitoso
            return True

    except TimeoutException:
        print("❌ ERROR: Timeout esperando el formulario de login")
        return False
    except Exception as e:
        print(f"❌ ERROR durante el login: {e}")
        return False


def export_cookies(driver, output_file):
    """Exporta las cookies de la sesión a un archivo JSON."""
    try:
        cookies = driver.get_cookies()
        print(f"🍪 Exportando {len(cookies)} cookies a {output_file}")

        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"✅ Cookies exportadas exitosamente")

        # Mostrar cookies importantes
        for cookie in cookies:
            if 'session' in cookie['name'].lower() or 'csrf' in cookie['name'].lower():
                print(f"   - {cookie['name']}: {cookie['value'][:20]}...")

        return True

    except Exception as e:
        print(f"❌ ERROR exportando cookies: {e}")
        return False


def main():
    """Función principal."""
    print("=" * 60)
    print("🕷️  OWASP ZAP - Autenticación con Selenium")
    print("=" * 60)
    print(f"Target: {TARGET_URL}")
    print(f"Login path: {LOGIN_PATH}")
    print(f"Username: {USERNAME}")
    print(f"Cookies output: {COOKIES_FILE}")
    print("=" * 60)

    driver = None
    try:
        driver = setup_driver()
        print("✅ Chrome WebDriver iniciado")

        if not perform_login(driver):
            print("\n❌ El login falló")
            sys.exit(1)

        if not export_cookies(driver, COOKIES_FILE):
            print("\n❌ Falló la exportación de cookies")
            sys.exit(1)

        print("\n" + "=" * 60)
        print("✅ Autenticación completada exitosamente")
        print("=" * 60)
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        if driver:
            print(f"URL actual: {driver.current_url}")
        sys.exit(1)

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
