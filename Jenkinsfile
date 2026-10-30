
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                bat '"C:\\Users\\lekha\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" --version'

                bat '"C:\\Users\\lekha\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m pip install -r app\\requirements.txt pytest'

                bat '"C:\\Users\\lekha\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m pytest -q app'
            }
        }

        stage('Build Docker Images') {
            steps {
                bat 'docker --version'

                bat 'docker build -t medical-store:v1 --build-arg APP_VERSION=v1 app'

                bat 'docker build -t medical-store:v2 --build-arg APP_VERSION=v2 app'

                bat 'docker build -t medical-store:v3 --build-arg APP_VERSION=v3 app'
            }
        }

        stage('Push to DockerHub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    bat 'echo %DH_TOKEN%| docker login -u %DH_USER% --password-stdin'

                    bat 'docker tag medical-store:v1 %DH_USER%/medical-store:v1'
                    bat 'docker tag medical-store:v2 %DH_USER%/medical-store:v2'
                    bat 'docker tag medical-store:v3 %DH_USER%/medical-store:v3'

                    bat 'docker push %DH_USER%/medical-store:v1'
                    bat 'docker push %DH_USER%/medical-store:v2'
                    bat 'docker push %DH_USER%/medical-store:v3'

                    bat 'docker logout'
                }
            }
        }
    }

    post {
        success {
            echo 'All three Medical Store versions built and pushed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}
