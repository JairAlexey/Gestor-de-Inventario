pipeline {
  agent any
  options { timestamps() }

  environment {
    VENV_DIR = '.venv'
    PY311 = 'C:\\Users\\Alienware\\AppData\\Local\\Programs\\Python\\Python311\\python.exe'
    PY = '.\\.venv\\Scripts\\python'
    PIP = '.\\.venv\\Scripts\\pip'
    DJANGO_SETTINGS_MODULE = 'gestor_inventario.settings_ci'
    PIP_DISABLE_PIP_VERSION_CHECK = '1'
    PYTHONIOENCODING = 'utf-8'

    // canal de Slack donde quieres las notificaciones
    SLACK_CHANNEL = '#nuevo-canal'
  }

  stages {

    stage('Build & Migrate') {
      steps {
        // Para debug: ver en qué rama estamos
        echo "🚀 Ejecutando en rama: ${env.BRANCH_NAME}"

        checkout scm
        bat """
          rem -- Crear / reusar venv y preparar dependencias
          py -3 --version || echo Python no disponible

          if not exist %VENV_DIR% (
            "%PY311%" -m venv %VENV_DIR%
          )

          %PY% -m pip install --upgrade pip

          if exist requirements.txt (
            %PIP% install -r requirements.txt
          ) else (
            %PIP% install Django pytest pytest-django pytest-cov flake8
          )

          rem -- Migraciones Django
          %PY% manage.py migrate --noinput --settings=%DJANGO_SETTINGS_MODULE%
        """
      }
    }

    stage('Lint') {
      options { timeout(time: 5, unit: 'MINUTES') }
      steps {
        bat ".\\.venv\\Scripts\\flake8 tasks gestor_inventario"
      }
    }

    stage('Tests') {
      options { timeout(time: 15, unit: 'MINUTES') }
      steps {
        bat """
          if not exist reports mkdir reports
          .\\.venv\\Scripts\\pytest --ds=%DJANGO_SETTINGS_MODULE% ^
            --junitxml=reports\\junit.xml ^
            --cov=. --cov-report=xml:reports\\coverage.xml
        """
      }
      post {
        always {
          junit 'reports/junit.xml'
          archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
      }
    }

    stage('SonarCloud Analysis') {
      steps {
        withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
          bat 'sonar-scanner -Dsonar.login=%SONAR_TOKEN%'
        }
      }
    }

    /***************************
     * STAGE: Publish (SOLO master)
     ***************************/
    stage('Publish ZIP') {
      when {
        expression { env.BRANCH_NAME == 'master' }
      }
      options { timeout(time: 5, unit: 'MINUTES') }
      steps {
        bat """
          rem -- collectstatic para empaquetar assets
          if exist staticfiles rmdir /S /Q staticfiles
          %PY% manage.py collectstatic --noinput --settings=%DJANGO_SETTINGS_MODULE%

          rem -- crear carpeta dist y comprimir todo en build.zip (artefacto)
          if not exist dist mkdir dist
          powershell -NoProfile -Command "Compress-Archive -Path * -DestinationPath dist\\build.zip -Force"
        """
        archiveArtifacts artifacts: 'dist/build.zip', allowEmptyArchive: false
      }
    }

    /***************************
     * STAGE: Deploy simulado (SOLO master)
     ***************************/
    stage('Deploy (simulado)') {
      when {
        expression { env.BRANCH_NAME == 'master' }
      }
      options { timeout(time: 2, unit: 'MINUTES') }
      steps {
        bat """
          rem Lanzar Django en background en 127.0.0.1:8000
          start "" /B %PY% manage.py runserver 127.0.0.1:8000 --settings=%DJANGO_SETTINGS_MODULE%

          rem Esperar 10s sin usar timeout.exe (que rompe en Jenkins)
          powershell -NoProfile -Command "Start-Sleep -Seconds 10"

          rem Hacer smoke test al home. Si falla, no rompas el build aquí.
          curl -s -o NUL -w "HTTP %%{http_code}\\n" http://127.0.0.1:8000/ || (echo curl_failed & exit /b 0)

          rem Matar proceso en el puerto 8000
          for /f "tokens=5" %%p in ('netstat -ano ^| find ":8000" ^| find "LISTENING"') do taskkill /PID %%p /F

          echo Smoke deploy OK
        """
      }
    }
  }

  /***************************
   * POST (Slack por rama)
   ***************************/
  post {

    // Siempre avisa a GitHub u otros sistemas si quieres integrar algo después;
    // por ahora no hacemos githubNotify explícito porque Slack ya está cubriendo visibilidad.

    success {
      script {
        def branch = env.BRANCH_NAME ?: 'master'  // fallback por si acaso

        if (branch.startsWith('feature/')) {
          // feature/* => NO correos (=> no Slack)
          echo "✔ Build OK en '${branch}' (sin notificación Slack por política feature/*)"

        } else if (branch == 'develop') {
          // develop => Slack SOLO si SUCCESS
          slackSend(
            channel: env.SLACK_CHANNEL,
            message: "✅ SUCCESS develop: ${env.JOB_NAME} #${env.BUILD_NUMBER} (${env.BUILD_URL})",
            tokenCredentialId: 'slack-token',
            teamDomain: 'ruedarosero'
          )

        } else if (branch.startsWith('hotfix/')) {
          // hotfix/* => SUCCESS/FAILURE a PROD_NOTIFY (aquí usamos el mismo canal)
          slackSend(
            channel: env.SLACK_CHANNEL,
            message: "🩹 HOTFIX OK: ${env.JOB_NAME} #${env.BUILD_NUMBER} (${branch}) ✅ ${env.BUILD_URL}",
            tokenCredentialId: 'slack-token',
            teamDomain: 'ruedarosero'
          )

        } else if (branch == 'master') {
          // master => SUCCESS/FAILURE a PROD_NOTIFY (mismo canal)
          slackSend(
            channel: env.SLACK_CHANNEL,
            message: "🚀 MASTER DEPLOY OK: ${env.JOB_NAME} #${env.BUILD_NUMBER} ✅ ${env.BUILD_URL}",
            tokenCredentialId: 'slack-token',
            teamDomain: 'ruedarosero'
          )

        } else {
          // cualquier otra rama (por si acaso)
          echo "Build OK en rama ${branch} (rama no categorizada)"
        }
      }
    }

    failure {
      script {
        def branch = env.BRANCH_NAME ?: 'master'

        if (branch.startsWith('feature/')) {
          // feature/* => sin correos incluso si falla
          echo "❌ Build FAILED en '${branch}' (sin notificación Slack por política feature/*)"

        } else if (branch == 'develop') {
          // develop => solo SUCCESS manda Slack, así que aquí no mandamos nada
          echo "❌ Build FAILED en develop (sin Slack porque develop solo avisa en SUCCESS)"

        } else if (branch.startsWith('hotfix/')) {
          // hotfix/* => SUCCESS/FAILURE avisa
          slackSend(
            channel: env.SLACK_CHANNEL,
            message: "🔥 HOTFIX FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER} (${branch}) ❌ ${env.BUILD_URL}",
            tokenCredentialId: 'slack-token',
            teamDomain: 'ruedarosero'
          )

        } else if (branch == 'master') {
          // master => SUCCESS/FAILURE avisa
          slackSend(
            channel: env.SLACK_CHANNEL,
            message: "💥 MASTER FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER} ❌ ${env.BUILD_URL}",
            tokenCredentialId: 'slack-token',
            teamDomain: 'ruedarosero'
          )

        } else {
          // fallback
          slackSend(
            channel: env.SLACK_CHANNEL,
            message: "⚠️ Build FAILED en rama ${branch}: ${env.JOB_NAME} #${env.BUILD_NUMBER} ${env.BUILD_URL}",
            tokenCredentialId: 'slack-token',
            teamDomain: 'ruedarosero'
          )
        }
      }
    }
  }
}
