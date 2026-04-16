pipeline {
agent any

environment {
    DOCKERHUB_CREDENTIALS = 'dockerhub-creds'
    IMAGE_NAME = 'priteshk13/devops-app'
}

stages {

    stage('Checkout Code') {
        steps {
           git branch: 'main', url: 'https://github.com/PriteshK13/devops-app.git'
        }
    }

    stage('Build Docker Image') {
        steps {
            sh 'docker build -t $IMAGE_NAME:latest .'
        }
    }

    stage('Login to DockerHub') {
        steps {
            withCredentials([usernamePassword(
                credentialsId: 'dockerhub-creds',
                usernameVariable: 'USERNAME',
                passwordVariable: 'PASSWORD'
            )]) {
                sh 'echo $PASSWORD | docker login -u $USERNAME --password-stdin'
            }
        }
    }

    stage('Push Image') {
        steps {
            sh 'docker push $IMAGE_NAME:latest'
        }
    }
}

}