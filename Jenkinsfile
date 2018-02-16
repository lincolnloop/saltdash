pipeline {
  agent any
  stages {
    stage('Prep') {
      agent any
      steps {
        sh 'mkdir -p _dist'
      }
    }
    stage('Build') {
      agent {
        docker {
          image 'ipmb/ubuntu-python-build:latest'
          args '-u root'
        }
        
      }
      steps {
        sh '/build.sh .'
        archiveArtifacts '/dist/*.tar.gz'
      }
    }
    stage('Test') {
      agent {
        docker {
          image 'ipmb/ubuntu-python-clean:latest'
        }
        
      }
      environment {
        SECRET_KEY = 'not-secret'
        ALLOWED_HOSTS = '*'
      }
      steps {
        sh '/test.sh /dist/*.tar.gz'
      }
    }
  }
}