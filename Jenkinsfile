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
        sh 'chown -R 112:116 .'
        archiveArtifacts(artifacts: '_dist/*.tar.gz', onlyIfSuccessful: true)
        stash(name: 'platter', includes: '_dist/*.tar.gz')
      }
    }
    stage('Test') {
      agent {
        docker {
          image 'ipmb/ubuntu-python-clean:latest'
          args '-u root'
        }
        
      }
      environment {
        SECRET_KEY = 'not-secret'
        ALLOWED_HOSTS = '*'
      }
      steps {
        unstash 'platter'
        sh '/test.sh ${WORKSPACE}/_dist/*.tar.gz'
      }
    }
  }
}