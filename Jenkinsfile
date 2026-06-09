pipeline {
    agent { label 'Agent-1' } // Exécution stricte sur votre agent nommé Agent-1
    
    triggers {
        githubPush() // Déclenchement 100% automatisé par le webhook GitHub
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
        
        stage('SAST - SonarQube via Conteneur Java 25') {
            steps {
                echo "=== Lancement analyse SonarQube dans un environnement Java 25 ==="
                withCredentials([string(credentialsId: 'webgoat-token', variable: 'SONAR_TOKEN')]) {
                    // RESOLUTION : Utilisation d'une image Maven embarquant nativement Java 25 pour éviter le crash du compilateur
                    sh '''
                        docker run --rm --network host \
                        -v "${WORKSPACE}:/usr/src" \
                        -w /usr/src \
                        maven:3.9-eclipse-temurin-25 \
                        mvn clean verify sonar:sonar \
                        -Dsonar.projectKey=webgoat-sast \
                        -Dsonar.host.url=http://127.0.0.1:9000 \
                        -Dsonar.token=${SONAR_TOKEN} \
                        -Dmaven.test.skip=true \
                        -Dsonar.scm.disabled=true
                    '''
                }
            }
        }
        
        stage('Export - Rapport HTML') {
            steps {
                echo "=== Génération du Rapport d'Anomalies au format HTML ==="
                withCredentials([string(credentialsId: 'webgoat-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        # Extraction des vulnérabilités au format JSON brut via l'API SonarQube
                        curl -s -u ${SONAR_TOKEN}: "http://127.0.0" -o raw_issues.json
                        
                        # Construction dynamique de la structure de la page HTML
                        echo "<html><head><style>
                            body { font-family: Arial, sans-serif; margin: 30px; background-color: #f4f6f9; }
                            h1 { color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }
                            .summary { background: #fff; padding: 15px; border-left: 5px solid #e74c3c; margin-bottom: 20px; border-radius: 4px; }
                            table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                            th { background-color: #34495e; color: white; }
                            tr:hover { background-color: #f9f9f9; }
                            .severity-CRITICAL { color: #c0392b; font-weight: bold; }
                            .severity-MAJOR { color: #d35400; font-weight: bold; }
                        </style></head><body>" > rapport_sast.html
                        
                        echo "<h1>Rapport de Sécurité SAST - Projet WebGoat</h1>" >> rapport_sast.html
                        echo "<div class='summary'><p><strong>Statut :</strong> Analyse Terminée avec Succès</p><p><strong>Outil :</strong> SonarQube Maven Plugin</p></div>" >> rapport_sast.html
                        echo "<table><tr><th>Composant / Fichier</th><th>Message de la Faille</th><th>Sévérité</th><th>Règle</th></tr>" >> rapport_sast.html
                        
                        # Extraction des lignes clés du JSON pour alimenter le tableau HTML
                        cat raw_issues.json | grep -o '"component":"[^"]*","project":"[^"]*","message":"[^"]*","severity":"[^"]*","rule":"[^"]*"' | while read -r line; do
                            component=$(echo "$line" | sed -E 's/.*"component":"([^"]*)".*/\\1/' | cut -d':' -f2)
                            message=$(echo "$line" | sed -E 's/.*"message":"([^"]*)".*/\1/')
                            severity=$(echo "$line" | sed -E 's/.*"severity":"([^"]*)".*/\1/')
                            rule=$(echo "$line" | sed -E 's/.*"rule":"([^"]*)".*/\1/')
                            
                            echo "<tr><td>$component</td><td>$message</td><td class='severity-$severity'>$severity</td><td>$rule</td></tr>" >> rapport_sast.html
                        done
                        
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
            cleanWs() // Nettoyage propre de l'espace de travail sur Agent-1
        }
    }
}
