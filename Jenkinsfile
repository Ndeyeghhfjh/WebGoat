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

        // ─────────────────────────────────────────────
        // ETAPE 1 : Recuperation du code source
        // ─────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '=== Recuperation du code source ==='
                checkout scm
            }
        }

        // ─────────────────────────────────────────────
        // ETAPE 2 : Analyse SAST avec SonarQube
        // ─────────────────────────────────────────────
        stage('SAST - SonarQube') {
            steps {
                echo '=== Lancement analyse SonarQube ==='
                sh '''
                    sudo docker run --rm \
                        --network host \
                        -v $WORKSPACE:/usr/src \
                        sonarsource/sonar-scanner-cli \
                        -Dsonar.projectKey=${PROJECT_KEY} \
                        -Dsonar.sources=. \
                        -Dsonar.exclusions=**/node_modules/**,**/*.xml,**/test/** \
                        -Dsonar.host.url=${SONAR_URL} \
                        -Dsonar.token=${SONAR_TOKEN}
                '''
                echo "=== Resultats : ${SONAR_URL}/dashboard?id=${PROJECT_KEY} ==="
            }
        }

        // ─────────────────────────────────────────────
        // ETAPE 3 : Export des resultats en CSV
        // ─────────────────────────────────────────────
        stage('Export - Rapport CSV') {
            steps {
                echo '=== Export des issues SonarQube ==='
                sh '''
                    curl -s -u admin:${SONAR_TOKEN} \
                        "${SONAR_URL}/api/issues/search?projectKeys=${PROJECT_KEY}&ps=500&p=1" \
                        -o result1.json

                    curl -s -u admin:${SONAR_TOKEN} \
                        "${SONAR_URL}/api/issues/search?projectKeys=${PROJECT_KEY}&ps=500&p=2" \
                        -o result2.json

                    python3 -c "
import json
issues = []
for f in ['result1.json', 'result2.json']:
    try:
        with open(f) as fp:
            issues.extend(json.load(fp).get('issues', []))
    except:
        pass
print('Severite,Message,Fichier,Ligne')
for i in issues:
    msg = i.get('message', '').replace(',', ';')
    print(f\"{i.get('severity')},{msg},{i.get('component')},{i.get('line', '')}\")
" > rapport_webgoat.csv

                    echo "=== Issues exportees : \$(wc -l < rapport_webgoat.csv) lignes ==="
                '''
                archiveArtifacts artifacts: '*.csv,*.json', fingerprint: true
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
Build      : ${BUILD_NUMBER}
Job        : ${JOB_NAME}
Status     : SUCCES
Commit     : ${env.GIT_COMMIT ?: 'N/A'}
Rapport    : ${BUILD_URL}artifact/rapport_webgoat.csv
Logs       : ${BUILD_URL}console
                        """
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
Build      : ${BUILD_NUMBER}
Job        : ${JOB_NAME}
Status     : ECHEC
Commit     : ${env.GIT_COMMIT ?: 'N/A'}
Logs       : ${BUILD_URL}console
                        """
                    )
                } catch(Exception e) {
                    echo "Email non envoye : ${e.message}"
                }
            }
        }
        always {
            node('built-in') {
                sh 'sudo docker system prune -f || true'
                echo '=== Nettoyage Docker termine ==='
            }
        }
    }
}
