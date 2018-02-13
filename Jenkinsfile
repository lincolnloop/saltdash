pipeline {
  agent any
  stages {
    stage('Prep') {
      agent any
      steps {
        pwd()
        sh 'mkdir -p _dist'
      }
    }
    stage('Build') {
      agent {
        docker {
          image 'ipmb/ubuntu-python-build:latest'
          args '-v _dist:/dist -v .:/code'
        }
        
      }
      steps {
        sh '""'
      }
    }
    stage('Test') {
      agent {
        docker {
          image 'ipmb/ubuntu-python-clean:latest'
          args '-v _dist:/dist'
        }
        
      }
      steps {
        sh '/dist/*.tar.gz'
      }
    }
  }
}