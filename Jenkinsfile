pipeline {
  agent any
  stages {
    stage('Build') {
      agent {
        docker {
          image 'ipmb/ubuntu-python-build:latest'
          args '-u root'
        }
        
      }
      steps {
        sh '/build.sh .'
        sh 'mv /dist _dist'
        sh 'chown -r 112:116 .'
        archiveArtifacts(artifacts: '_dist/*.tar.gz', onlyIfSuccessful: true)
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
        sh '/test.sh _dist/*.tar.gz'
      }
    }
  }
}