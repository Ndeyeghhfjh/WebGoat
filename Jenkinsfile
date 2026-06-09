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
                        -v $WORKSPACE:/usr/src \
                        sonarsource/sonar-scanner-cli \
                        -Dsonar.projectKey=webgoat-sast \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.token=$SONAR_TOKEN
                '''
            }
        }

        stage('Export - Rapport HTML') {
            steps {
                echo '=== Generation du rapport ==='
                sh '''
                    curl -s -u admin:admin \
                        "http://localhost:9000/api/issues/search?projectKeys=webgoat-sast&ps=500&p=1" \
                        -o result1.json

                    curl -s -u admin:admin \
                        "http://localhost:9000/api/issues/search?projectKeys=webgoat-sast&ps=500&p=2" \
                        -o result2.json

                    python3 /home/jenkins/juice-shop/generate_pdf.py || true
                    cp rapport_sonarqube.pdf rapport_webgoat.pdf || true
                '''

                archiveArtifacts artifacts: '*.pdf,*.json', fingerprint: true
            }
        }
    }

    post {
        always {
            emailext(
                to: 'astoudieng941@gmail.com',
                subject: "[Jenkins] Build #${BUILD_NUMBER} - ${currentBuild.currentResult}",
                body: """
Build       : ${BUILD_NUMBER}
Job         : ${JOB_NAME}
Status      : ${currentBuild.currentResult}
Commit      : ${GIT_COMMIT}
Rapport     : ${BUILD_URL}artifact/rapport_webgoat.pdf
Logs        : ${BUILD_URL}console
                """,
                attachmentsPattern: '*.pdf'
            )
        }

        success {
            echo '=== Build reussi ==='
        }

        failure {
            echo '=== Build echoue ==='
        }
    }
}