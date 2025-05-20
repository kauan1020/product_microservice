name: CI/CD Pipeline

on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master ]

jobs:
  test-and-build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Necessário para o SonarQube analisar histórico

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: 1.5.1
          virtualenvs-create: true
          virtualenvs-in-project: true

      - name: Cache Poetry dependencies
        uses: actions/cache@v3
        with:
          path: .venv
          key: ${{ runner.os }}-poetry-${{ hashFiles('**/poetry.lock') }}
          restore-keys: |
            ${{ runner.os }}-poetry-

      - name: Install dependencies
        run: |
          poetry install --no-interaction --no-root
          poetry add pytest-cov behave coverage --group dev

      - name: Run unit tests with coverage
        run: |
          cd tech
          poetry run pytest tests --cov=. --cov-report=xml:../coverage.xml --cov-report=term
          cd ..

      - name: Run BDD tests with Behave
        run: |
          cd tech
          poetry run behave tests/tech/bdd/features/
          cd ..

      - name: SonarQube Scan
        uses: SonarSource/sonarqube-scan-action@master
        env:
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          args: >
            -Dsonar.projectKey=products_microservice
            -Dsonar.projectName="Products Microservice"
            -Dsonar.sources=tech
            -Dsonar.python.coverage.reportPaths=coverage.xml
            -Dsonar.exclusions=**/__pycache__/**,**/tests/**,**/*.html,**/htmlcov/**
            -Dsonar.coverage.exclusions=tests/**/*,**/test_*.py,**/__init__.py

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-session-token: ${{ secrets.AWS_SESSION_TOKEN }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            131793876715.dkr.ecr.us-east-1.amazonaws.com/microservices/products:latest
            131793876715.dkr.ecr.us-east-1.amazonaws.com/microservices/products:${{ github.sha }}
          platforms: linux/amd64
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            POETRY_VERSION=1.5.1

  deploy:
    needs: test-and-build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-session-token: ${{ secrets.AWS_SESSION_TOKEN }}
          aws-region: us-east-1

      - name: Install kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'

      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name tech-eks-cluster --region us-east-1

      - name: Deploy to Kubernetes
        run: |
          kubectl get namespace products || kubectl create namespace products
          
          # Use o latest tag no deploy
          kubectl set image deployment/products-service products-service=131793876715.dkr.ecr.us-east-1.amazonaws.com/microservices/products:latest -n products || kubectl apply -f k8s/deployment.yaml
          
          # Verifique se o serviço já existe, senão, aplique-o
          if [ -f k8s/service.yaml ]; then
            kubectl apply -f k8s/service.yaml
          fi
          
          # Verifique o status do rollout
          kubectl rollout status deployment/products-service -n products --timeout=300s