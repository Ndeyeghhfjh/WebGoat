pipeline {

    agent any

    environment {
        SONAR_URL   = 'http://localhost:9000'
        PROJECT_KEY = 'webgoat-sast'
        SONAR_TOKEN = credentials('sonar-token')
    }

    triggers {
        githubPush()
    }

    stages {

        stage('Checkout') {
            steps {
                echo '=== Recuperation du code ==='
                checkout scm
            }
        }

        stage('SAST - SonarQube') {
            steps {
                echo '=== Analyse SonarQube ==='
                sh '''
                    docker run --rm --network host \
                        -v \C:\Users\HP\WebGoat:/usr/src \
                        sonarsource/sonar-scanner-cli \
                        -Dsonar.projectKey=webgoat-sast \
                        -Dsonar.sources=src/main \
                        -Dsonar.exclusions=**/test/**,**/*.xml \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.token=\
                '''
            }
        }

        stage('Export - Rapport HTML') {
            steps {
                echo '=== Generation du rapport ==='
                sh '''
                    curl -s -u admin:\ \
                        "\/api/issues/search?projectKeys=\&ps=500&p=1" \
                        -o result1.json
                    curl -s -u admin:\ \
                        "\/api/issues/search?projectKeys=\&ps=500&p=2" \
                        -o result2.json
                    python3 /home/jenkins/juice-shop/generate_pdf.py
                    cp rapport_sonarqube.pdf \/rapport_webgoat.pdf || true
                '''
                archiveArtifacts artifacts: '*.pdf,*.json', fingerprint: true
            }
        }
    }

    post {
        always {
            emailext(
                to: 'ndeyeastoudieng@esp.sn',
                subject: "[Jenkins] \ — \ #\",
                body: """
Build       : \
Job         : \
Build #     : \
Commit      : \
Rapport     : \artifact/rapport_webgoat.pdf
Logs        : \console
                """,
                attachmentsPattern: '*.pdf'
            )
        }
        success { echo '=== Build reussi ===' }
        failure { echo '=== Build echoue ===' }
    }
}
