pipeline {
    agent any

    environment {
        SONAR_URL   = 'http://localhost:9000'
        PROJECT_KEY = 'webgoat-sast'
        SONAR_TOKEN = credentials('webgoat-token')
    }

    triggers {
        githubPush()
    }

    stages {

        stage('Checkout') {
            steps {
                echo '=== Recuperation du code source ==='
                checkout scm
            }
        }

        stage('SAST - SonarQube') {
            steps {
                echo '=== Lancement analyse SonarQube ==='
                sh '''
                    docker run --rm --network host \
                        -v $WORKSPACE:/usr/src \
                        sonarsource/sonar-scanner-cli \
                        -Dsonar.projectKey=webgoat-sast \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.token=$SONAR_TOKEN \
                        -Dsonar.scm.disabled=true
                '''
            }
        }

        stage('Export - Rapport CSV') {
            steps {
                echo '=== Export des issues SonarQube ==='

                sh '''
                    curl -s -u ${SONAR_TOKEN}: \
                    "${SONAR_URL}/api/issues/search?projectKeys=${PROJECT_KEY}&ps=500&p=1" \
                    -o result1.json

                    curl -s -u ${SONAR_TOKEN}: \
                    "${SONAR_URL}/api/issues/search?projectKeys=${PROJECT_KEY}&ps=500&p=2" \
                    -o result2.json
                '''

                writeFile file: 'gen.py', text: '''
import json

issues = []

for f in ["result1.json", "result2.json"]:
    try:
        with open(f) as fp:
            data = json.load(fp)
            issues.extend(data.get("issues", []))
    except:
        pass

with open("rapport_webgoat.csv", "w") as out:
    out.write("Severity,Message,File,Line\\n")
    for i in issues:
        msg = i.get("message", "").replace(",", ";")
        out.write(f"{i.get('severity','')},{msg},{i.get('component','')},{i.get('line','')}\\n")

print("Issues exportees:", len(issues))
'''

                sh 'python3 gen.py'
                archiveArtifacts artifacts: 'rapport_webgoat.csv,result*.json', fingerprint: true
            }
        }
    }

    post {
        success {
            echo '=== Build reussi ==='
            script {
                try {
                    emailext(
                        to: 'astoudieng941@gmail.com',
                        subject: "[Jenkins] Build #${BUILD_NUMBER} - SUCCES",
                        body: """
Build   : ${BUILD_NUMBER}
Job     : ${JOB_NAME}
Status  : SUCCES
Rapport : ${BUILD_URL}artifact/rapport_webgoat.csv
                        """,
                        attachmentsPattern: 'rapport_webgoat.csv',
                        mimeType: 'text/plain'
                    )
                } catch(Exception e) {
                    echo "Email non envoye : ${e.message}"
                }
            }
        }

        failure {
            echo '=== Build echoue ==='
            script {
                try {
                    emailext(
                        to: 'astoudieng941@gmail.com',
                        subject: "[Jenkins] Build #${BUILD_NUMBER} - ECHEC",
                        body: """
Build   : ${BUILD_NUMBER}
Job     : ${JOB_NAME}
Status  : ECHEC
Logs    : ${BUILD_URL}console
                        """,
                        mimeType: 'text/plain'
                    )
                } catch(Exception e) {
                    echo "Email non envoye : ${e.message}"
                }
            }
        }

        always {
            echo '=== Nettoyage Docker ==='
            sh 'docker system prune -f || true'
        }
    }
}