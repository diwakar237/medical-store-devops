pipeline {
  agent any
  environment { DOCKERHUB_USER = 'YOUR_DOCKERHUB_USERNAME' }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Test') {
      steps { sh 'python3 -m pip install -r app/requirements.txt pytest && cd app && pytest -q' }
    }
    stage('Build and Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_TOKEN')]) {
          sh 'echo "$DH_TOKEN" | docker login -u "$DH_USER" --password-stdin'
          sh 'for v in v1 v2 v3; do docker build -t "$DH_USER/medical-store:$v" --build-arg APP_VERSION=$v app && docker push "$DH_USER/medical-store:$v"; done'
          sh 'docker logout'
        }
      }
    }
    stage('Deploy') {
      steps {
        withCredentials([file(credentialsId: 'minikube-kubeconfig', variable: 'KCFG')]) {
          sh 'export KUBECONFIG="$KCFG"; kubectl apply -f k8s/postgres.yaml; kubectl apply -f k8s/postgres-service.yaml; kubectl rollout status deployment/postgres --timeout=180s'
          sh 'export KUBECONFIG="$KCFG"; for v in v1 v2 v3; do sed "s|DOCKERHUB_USERNAME|$DOCKERHUB_USER|g" k8s/$v-deployment.yaml | kubectl apply -f -; kubectl apply -f k8s/$v-service.yaml; done'
        }
      }
    }
  }
  post { success { echo 'Medical Store V1, V2 and V3 deployed.' } }
}
