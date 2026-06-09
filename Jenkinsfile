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
echo '=== Verification du workspace ==='

    sh '''
        pwd
        ls -la
        find . -type f | head -50
    '''

    echo '=== Lancement analyse SonarQube ==='

    sh '''
        docker run --rm \
            --network host \
            -v "$WORKSPACE:/usr/src" \
            sonarsource/sonar-scanner-cli \
            -Dsonar.projectKey=${PROJECT_KEY} \
            -Dsonar.sources=. \
            -Dsonar.exclusions=**/node_modules/**,**/target/**,**/.git/** \
            -Dsonar.host.url=${SONAR_URL} \
            -Dsonar.token=${SONAR_TOKEN} \
            -Dsonar.scm.disabled=true
    '''
}
       stage('Export - Rapport CSV') {
steps {
echo '=== Export des issues SonarQube ==='

```
    sh '''
        curl -s -u ${SONAR_TOKEN}: \
        "${SONAR_URL}/api/issues/search?projectKeys=${PROJECT_KEY}&ps=500&p=1" \
        -o result1.json

        echo "=== Aperçu result1.json ==="
        head -20 result1.json

        curl -s -u ${SONAR_TOKEN}: \
        "${SONAR_URL}/api/issues/search?projectKeys=${PROJECT_KEY}&ps=500&p=2" \
        -o result2.json
    '''

    writeFile file: 'gen.py', text: '''
```

import json

issues = []

for f in ["result1.json", "result2.json"]:
try:
with open(f, "r", encoding="utf-8") as fp:
data = json.load(fp)
issues.extend(data.get("issues", []))
except Exception as e:
print("Erreur:", e)

with open("rapport_webgoat.csv", "w", encoding="utf-8") as out:
out.write("Severity,Message,File,Line\n")

```
for i in issues:
    msg = i.get("message", "").replace(",", ";")
    out.write(
        f"{i.get('severity','')},"
        f"{msg},"
        f"{i.get('component','')},"
        f"{i.get('line','')}\\n"
    )
```

print(f"Issues exportees: {len(issues)}")
'''

```
    sh 'python3 gen.py'

    sh 'wc -l rapport_webgoat.csv || true'

    archiveArtifacts artifacts: 'rapport_webgoat.csv,result*.json', fingerprint: true
}
```

}

    post {
        success {
            echo '=== Build reussi ==='
            script {
                try {
                    emailext(
                        to: 'astoudieng941@gmail.com',
                        subject: '[Jenkins] Build #' + BUILD_NUMBER + ' - SUCCES - ' + JOB_NAME,
                        body: 'Build: ' + BUILD_NUMBER + '\nJob: ' + JOB_NAME + '\nStatus: SUCCES\nRapport: ' + BUILD_URL + 'artifact/rapport_webgoat.csv\nLogs: ' + BUILD_URL + 'console',
                        attachmentsPattern: 'rapport_webgoat.csv',
                        mimeType: 'text/plain'
                    )
                } catch(Exception e) {
                    echo 'Email non envoye : ' + e.message
                }
            }
        }
        failure {
            echo '=== Build echoue ==='
            script {
                try {
                    emailext(
                        to: 'astoudieng941@gmail.com',
                        subject: '[Jenkins] Build #' + BUILD_NUMBER + ' - ECHEC - ' + JOB_NAME,
                        body: 'Build: ' + BUILD_NUMBER + '\nJob: ' + JOB_NAME + '\nStatus: ECHEC\nLogs: ' + BUILD_URL + 'console',
                        mimeType: 'text/plain'
                    )
                } catch(Exception e) {
                    echo 'Email non envoye : ' + e.message
                }
            }
        }
        always {
            echo '=== Fin du pipeline ==='
            sh 'docker system prune -f || true'
        }
    }
}
