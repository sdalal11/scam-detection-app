pipeline {
    agent any
    
    environment {
        // Docker Hub credentials (stored in Jenkins credentials)
        DOCKER_HUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKER_HUB_USERNAME = 'sdalal11'
        IMAGE_NAME = 'scam-detection-api'
        
        // Build information
        BUILD_TAG = "${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(7)}"
        
        // Add Docker to PATH for macOS
        PATH = "/usr/local/bin:/Applications/Docker.app/Contents/Resources/bin:${env.PATH}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from repository...'
                checkout scm
                sh 'git log -1 --oneline'
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python environment...'
                dir('backend') {
                    sh '''
                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                dir('backend') {
                    sh '''
                        . .venv/bin/activate
                        python -m pytest -v --cov=. --cov-report=xml --cov-report=html --junitxml=test-results/junit.xml
                    '''
                }
            }
            post {
                always {
                    // Publish test results
                    junit allowEmptyResults: true, testResults: 'backend/test-results/junit.xml'
                    
                    // Publish coverage report
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'backend/htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
                failure {
                    echo 'Tests failed! Stopping pipeline.'
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                dir('backend') {
                    sh """
                        docker build -t ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${BUILD_TAG} .
                        docker tag ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${BUILD_TAG} ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest
                    """
                }
            }
        }
        
        stage('Test Docker Image') {
            steps {
                echo '🔍 Testing Docker image...'
                sh """
                    # Run container in background
                    docker run -d --name test-container-${BUILD_NUMBER} \
                        -e ELEVENLABS_API_KEY=test \
                        -e GEMINI_API_KEY=test \
                        -p 8080:8000 \
                        ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${BUILD_TAG}
                    
                    # Wait for container to start
                    sleep 10
                    
                    # Check if container is running
                    docker ps | grep test-container-${BUILD_NUMBER}
                    
                    # Test health endpoint
                    curl -f http://localhost:8080/health || exit 1
                    
                    echo "Docker image health check passed!"
                """
            }
            post {
                always {
                    // Clean up test container
                    sh """
                        docker stop test-container-${BUILD_NUMBER} || true
                        docker rm test-container-${BUILD_NUMBER} || true
                    """
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing Docker image to Docker Hub...'
                sh """
                    # Login to Docker Hub
                    echo \$DOCKER_HUB_CREDENTIALS_PSW | docker login -u \$DOCKER_HUB_CREDENTIALS_USR --password-stdin
                    
                    # Push both tagged and latest versions
                    docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${BUILD_TAG}
                    docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest
                    
                    echo "Image pushed: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${BUILD_TAG}"
                    echo "Image pushed: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest"
                """
            }
            post {
                always {
                    // Logout from Docker Hub
                    sh 'docker logout'
                }
            }
        }
        
        stage('Cleanup Local Images') {
            steps {
                echo '🧹 Cleaning up local Docker images...'
                sh """
                    docker rmi ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${BUILD_TAG} || true
                    docker system prune -f
                """
            }
        }
    }
    
    post {
        success {
            echo '''
            ========================================
            Pipeline completed successfully!
            ========================================
            '''
            echo "Docker Image: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${BUILD_TAG}"
            echo "Docker Hub: https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/${IMAGE_NAME}"
        }
        
        failure {
            echo '''
            ========================================
            Pipeline failed!
            ========================================
            '''
        }
        
        always {
            // Clean up workspace
            echo '🧹 Cleaning up workspace...'
            cleanWs()
        }
    }
}
