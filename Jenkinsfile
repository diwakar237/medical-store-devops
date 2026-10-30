
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\lekha\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'
        DOCKER = 'C:\\Users\\lekha\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                bat '"%PYTHON%" --version'
                bat '"%PYTHON%" -m pip install -r app\\requirements.txt pytest'
                bat '"%PYTHON%" -m pytest -q app'
            }
        }

        stage('Build Docker Images') {
            steps {
                bat '"%DOCKER%" --version'

                bat '"%DOCKER%" build -t medical-store:v1 --build-arg APP_VERSION=v1 app'
                bat '"%DOCKER%" build -t medical-store:v2 --build-arg APP_VERSION=v2 app'
                bat '"%DOCKER%" build -t medical-store:v3 --build-arg APP_VERSION=v3 app'
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
                    bat 'echo %DH_TOKEN%| "%DOCKER%" login -u %DH_USER% --password-stdin'

                    bat '"%DOCKER%" tag medical-store:v1 %DH_USER%/medical-store:v1'
                    bat '"%DOCKER%" tag medical-store:v2 %DH_USER%/medical-store:v2'
                    bat '"%DOCKER%" tag medical-store:v3 %DH_USER%/medical-store:v3'

                    bat '"%DOCKER%" push %DH_USER%/medical-store:v1'
                    bat '"%DOCKER%" push %DH_USER%/medical-store:v2'
                    bat '"%DOCKER%" push %DH_USER%/medical-store:v3'

                    bat '"%DOCKER%" logout'
                }
            }
        }
    }

    post {
        success {
            echo 'All three versions built and pushed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}
