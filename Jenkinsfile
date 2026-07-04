pipeline {
    agent any
    environment {
        DOCKER_IMAGE = "local-python-app"
        DEPLOY_USER = "ec2-user"
        SERVER_1 = "10.0.21.104"
        SERVER_2 = "10.0.41.193"
    }
    stages {
        stage('Pobieranie Kodu') {
            steps {
                checkout scm
            }
        }
        stage('Budowanie obrazu Docker') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:latest ."
            }
        }
        stage('Archiwizacja i transfer obrazu') {
            steps {
                sh "docker save ${DOCKER_IMAGE}:latest -o app.tar"
            }
        }
        stage('Wdrożenie na Serwer 1') {
            steps {
                sshagent(['aws-ssh-key']) {
                    sh """
                    scp -o StrictHostKeyChecking=no app.tar ${DEPLOY_USER}@${SERVER_1}:/home/ec2-user/
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${SERVER_1} '
                        sudo docker load -i /home/ec2-user/app.tar
                        sudo docker stop python-web-app || true
                        sudo docker rm python-web-app || true
                        sudo docker run -d -p 80:80 --name python-web-app ${DOCKER_IMAGE}:latest
                        rm /home/ec2-user/app.tar
                    '
                    """
                }
            }
        }
        stage('Wdrożenie na Serwer 2') {
            steps {
                sshagent(['aws-ssh-key']) {
                    sh """
                    scp -o StrictHostKeyChecking=no app.tar ${DEPLOY_USER}@${SERVER_2}:/home/ec2-user/
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${SERVER_2} '
                        sudo docker load -i /home/ec2-user/app.tar
                        sudo docker stop python-web-app || true
                        sudo docker rm python-web-app || true
                        sudo docker run -d -p 80:80 --name python-web-app ${DOCKER_IMAGE}:latest
                        rm /home/ec2-user/app.tar
                    '
                    """
                }
            }
        }
    }
}
