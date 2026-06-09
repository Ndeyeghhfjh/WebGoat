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
                    docker run --rm \
                        --network host \
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
                    curl -s -u admin:$SONAR_TOKEN \
                        "http://localhost:9000/api/issues/search?projectKeys=webgoat-sast&ps=500&p=1" \
                        -o result1.json
                    curl -s -u admin:$SONAR_TOKEN \
                        "http://localhost:9000/api/issues/search?projectKeys=webgoat-sast&ps=500&p=2" \
                        -o result2.json

                    cat > /tmp/gen.py << 'PYEOF'
import json
issues = []
for f in ["result1.json", "result2.json"]:
    try:
        with open(f) as fp:
            issues.extend(json.load(fp).get("issues", []))
    except Exception:
        pass
with open("rapport_webgoat.csv", "w") as out:
    out.write("Severity,Message,File,Line\n")
    for i in issues:
        msg = i.get("message", "").replace(",", ";")
        out.write(i.get("severity","") + "," + msg + "," + i.get("component","") + "," + str(i.get("line","")) + "\n")
print("Issues: " + str(len(issues)))
PYEOF

                    docker run --rm \
                        -v $WORKSPACE:/data \
                        -v /tmp/gen.py:/gen.py \
                        -w /data \
                        python:3.11-alpine \
                        python3 /gen.py
                '''
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
                        subject: "[Jenkins] Build #${BUILD_NUMBER} - SUCCES - ${JOB_NAME}",
                        body: """
Build   : ${BUILD_NUMBER}
Job     : ${JOB_NAME}
Status  : SUCCES
Commit  : ${env.GIT_COMMIT ?: 'N/A'}
Rapport : ${BUILD_URL}artifact/rapport_webgoat.csv
Logs    : ${BUILD_URL}console
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
                        subject: "[Jenkins] Build #${BUILD_NUMBER} - ECHEC - ${JOB_NAME}",
                        body: """
Build   : ${BUILD_NUMBER}
Job     : ${JOB_NAME}
Status  : ECHEC
Commit  : ${env.GIT_COMMIT ?: 'N/A'}
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
            echo '=== Fin du pipeline ==='
            sh 'docker system prune -f || true'
        }
    }
}