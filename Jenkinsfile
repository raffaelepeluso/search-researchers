pipeline {
    agent any
    stages {
        stage('build') {
            when {
                branch 'service-*'
            }
            steps {
                script {
                    docker.build("${env.BRANCH_NAME}", "${env.BRANCH_NAME}")
                }
            }
        }
        stage('test') {
            when {
                branch 'release-*'
            }
            steps {
                script {
                    sh 'docker compose up --abort-on-container-exit --exit-code-from newman'
                    sh 'docker compose down'
                 }
            }
        }
    }
}