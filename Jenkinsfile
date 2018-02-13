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
          args '-v ${env.WORKSPACE}_dist:/dist -v ${env.WORKSPACE}:/code'
        }
        
      }
      steps {
        sh '/build.sh'
      }
    }
    stage('Test') {
      agent {
        docker {
          image 'ipmb/ubuntu-python-clean:latest'
          args '-v ${env.WORKSPACE}/_dist:/dist'
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