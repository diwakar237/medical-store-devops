# Medical Store Management System — 24MIS0126

A beginner-friendly DevOps project using Flask, PostgreSQL, GitHub, Jenkins, Docker, DockerHub and Kubernetes.

## Three versions
- **V1** — Add medicine name, opening stock and unit price.
- **V2** — Update the quantity of an existing medicine.
- **V3** — View the shared medicine inventory.

All versions use one PostgreSQL database. Therefore, add an item in V1, update it in V2, then view the result in V3.

## Local development (Docker Compose)
Install Docker Desktop, open this folder in VS Code, then run:
```bash
docker compose up --build
```
Visit http://localhost:5001 (V1), http://localhost:5002 (V2), and http://localhost:5003 (V3).
Stop with `docker compose down`.

## GitHub branches and commits
Create an empty GitHub repository, then run these commands from the project folder:
```bash
git init
git add .
git commit -m "chore: add medical store project foundation"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/medical-store-devops.git
git push -u origin main

git switch -c v1
git add .
git commit -m "feat(v1): add medicine stock entry"
git push -u origin v1

git switch main
git switch -c v2
git add .
git commit -m "feat(v2): update medicine quantity"
git push -u origin v2

git switch main
git switch -c v3
git add .
git commit -m "feat(v3): view medicine inventory"
git push -u origin v3
```
This creates separate branches and version commits. If the assignment expects isolated branch histories, branch each version from the prior version or use cherry-pick according to your instructor's preferred workflow.

## DockerHub images
Create a DockerHub repository named `medical-store`. Replace the username:
```bash
docker login
docker build -t YOUR_DOCKERHUB_USERNAME/medical-store:v1 --build-arg APP_VERSION=v1 app
docker build -t YOUR_DOCKERHUB_USERNAME/medical-store:v2 --build-arg APP_VERSION=v2 app
docker build -t YOUR_DOCKERHUB_USERNAME/medical-store:v3 --build-arg APP_VERSION=v3 app
docker push YOUR_DOCKERHUB_USERNAME/medical-store:v1
docker push YOUR_DOCKERHUB_USERNAME/medical-store:v2
docker push YOUR_DOCKERHUB_USERNAME/medical-store:v3
```

## Kubernetes deployment using Minikube
Start Minikube:
```bash
minikube start
kubectl config current-context
```
Replace `DOCKERHUB_USERNAME` in `k8s/v1-deployment.yaml`, `v2-deployment.yaml`, and `v3-deployment.yaml` with your DockerHub username. Apply:
```bash
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/v1-deployment.yaml
kubectl apply -f k8s/v1-service.yaml
kubectl apply -f k8s/v2-deployment.yaml
kubectl apply -f k8s/v2-service.yaml
kubectl apply -f k8s/v3-deployment.yaml
kubectl apply -f k8s/v3-service.yaml
kubectl get deployments
kubectl get services
```
URLs:
- V1: http://localhost:30001
- V2: http://localhost:30002
- V3: http://localhost:30003

If localhost NodePort routing is not available with your Minikube driver, run each in a separate terminal:
```bash
minikube service medical-store-v1 --url
minikube service medical-store-v2 --url
minikube service medical-store-v3 --url
```

## Jenkins pipeline
The included `Jenkinsfile` tests the Flask app, builds and pushes Docker tags `v1`, `v2`, `v3`, and applies Kubernetes manifests.
1. Create a Jenkins Pipeline job connected to your GitHub repository.
2. Install Pipeline, Git and Credentials Binding plugins; ensure Docker CLI/daemon, Python 3, pip, and kubectl are available on the Jenkins agent.
3. Add Jenkins username/password credential ID `dockerhub-creds` (DockerHub username and access token).
4. Add Jenkins Secret file credential ID `minikube-kubeconfig` with a kubeconfig that is reachable from the Jenkins agent.
5. Replace `YOUR_DOCKERHUB_USERNAME` in the `Jenkinsfile` environment value.
6. Run the pipeline.

If Jenkins is containerized or runs on another machine, Docker daemon and Kubernetes API access must be configured for that agent. A kubeconfig using localhost may not work from a remote/containerized agent.

## Notes
The sample PostgreSQL credentials are for local coursework only. Use Kubernetes Secrets instead of plaintext credentials for any real deployment. This is a teaching demo, not a production pharmacy system; it does not include login, audit history, expiry tracking, prescription management or regulatory controls.
