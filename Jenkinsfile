pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "priteshk13/devops-app"
        TAG = "latest"
    }

    stages {

        stage('Clone Code') {
            steps {
                git 'https://github.com/PriteshK13/devops-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE:$TAG .'
            }
        }

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh 'echo $PASS | docker login -u $USER --password-stdin'
                    sh 'docker push $DOCKER_IMAGE:$TAG'
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh '''
                aws eks update-kubeconfig --region ap-south-1 --name devops-eks
                kubectl set image deployment/devops-app devops-app=$DOCKER_IMAGE:$TAG
                '''
            }
        }
    }
}