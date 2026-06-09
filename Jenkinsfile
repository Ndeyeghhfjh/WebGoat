pipeline {
    agent { label 'Agent-1' } // Exécution stricte sur l'Agent-1
    
    triggers {
        githubPush() // Déclenchement automatique par webhook GitHub lors d'un commit
    }
    
    environment {
        SONAR_SERVER = 'SonarQube'
        RECEIVER_EMAIL = 'astoudieng941@gmail.com'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "=== Récupération automatique du code source (WebGoat) ==="
                checkout scm
            }
        }
        
        stage('SAST - SonarQube Analyser') {
            steps {
                echo "=== Lancement analyse SonarQube du code source ==="
                withCredentials([string(credentialsId: 'webgoat-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        chmod +x ./mvnw
                        ./mvnw sonar:sonar \
                        -Dsonar.projectKey=webgoat-sast \
                        -Dsonar.host.url=http://127.0.0.1:9000 \
                        -Dsonar.token=${SONAR_TOKEN} \
                        -Dsonar.sources=src/main \
                        -Dsonar.java.binaries=. \
                        -Dsonar.scm.disabled=true \
                        -Dsonar.readiness.timeout=120
                    '''
                }
            }
        }
        
        stage('Export - Rapport HTML') {
            steps {
                echo "=== Génération du Rapport d'Anomalies au format HTML ==="
                withCredentials([string(credentialsId: 'webgoat-token', variable: 'SONAR_TOKEN')]) {
                    // CORRECTION : Utilisation de l'URL locale complète vers le port 9000 de SonarQube
                    sh '''
                        # 1. Récupération des issues SonarQube
                        curl -s -u ${SONAR_TOKEN}: \
                        "http://localhost:9000/api/issues/search?componentKeys=webgoat-sast&ps=500" \
                        -o raw_issues.json
                        
                        # 2. HTML header
                        echo "<html><head><style>
                        body { font-family: Arial; margin: 30px; background: #f4f6f9; }
                        table { width: 100%; border-collapse: collapse; }
                        th, td { border: 1px solid #ddd; padding: 10px; }
                        th { background: #2c3e50; color: white; }
                        </style></head><body>" > rapport_sast.html
                        
                        echo "<h1>Rapport SAST - WebGoat</h1>" >> rapport_sast.html
                        echo "<table><tr><th>Composant</th><th>Message</th><th>Sévérité</th><th>Règle</th></tr>" >> rapport_sast.html
                        
                        # 3. JSON → HTML
                        jq -r '.issues[] |
                            "<tr><td>" + .component + "</td><td>" + .message + "</td><td>" + .severity + "</td><td>" + .rule + "</td></tr>"' \
                            raw_issues.json >> rapport_sast.html
                        
                        # 4. fermeture HTML
                        echo "</table></body></html>" >> rapport_sast.html
                        '''
                }
            }
        }
    }
    
        post {
        always {
            echo "=== Envoi du rapport d'erreur HTML par Mail ==="
    
            catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                emailext (
                    to: "${env.RECEIVER_EMAIL}",
                    subject: "Rapport HTML SAST Automatique WebGoat - Build #${env.BUILD_NUMBER}",
                    body: """Bonjour l'équipe,
    
    Le pipeline de sécurité s'est déclenché automatiquement suite au commit sur GitHub.
    
    L'analyse statique du code de WebGoat est terminée. Vous trouverez en pièce jointe le rapport complet au format HTML.
    
    Statut de l'intégration : ${currentBuild.currentResult}
    👉 Accès à l'IHM SonarQube : http://localhost:9000/dashboard?id=webgoat-sast
    
    Cordialement,
    Votre Automation Agent-1.""",
                    attachmentsPattern: 'rapport_sast.html'
                )
            }
    
            // ✅ ARCHIVAGE DU RAPPORT (IMPORTANT)
            archiveArtifacts artifacts: 'rapport_sast.html', fingerprint: true

            cleanWs()             // nettoyage workspace
        }
    }
}   
    
