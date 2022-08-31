pipeline {
  agent {
    node {
      label 'maven'
    }

  }
  stages {
    stage('default-0') {
      parallel {
        stage('拉取代码') {
          agent none
          steps {
            git(credentialsId: 'gitlab-account', url: 'http://gitlab.xxx.com/lucumt-group/system.git', branch: '$BRANCH_NAME', changelog: true, poll: false)
            sh '''sed -i "s/10.30.5.150/10.30.5.170/g" app/src/main/resources/bootstrap.yml
echo "拉取代码成功"'''
          }
        }

        stage('识别系统环境') {
          agent none
          steps {
            script {
              switch(PRODUCT_PHASE) {
                case "sit":
                env.NODE_PORT = 13002
                break
                case "test":
                env.NODE_PORT = 14002
                break
                case "prod":
                env.NODE_PORT = 15002
                break
              }
            }

          }
        }

      }
    }

    stage('单元测试') {
      agent none
      steps {
        container('maven') {
          sh '''mvn clean compile test
echo "执行相关的单元测试"'''
          script {
            env.PROJECT_VERSION = sh(script: 'mvn help:evaluate -Dexpression=project.version -q -DforceStdout', returnStdout: true)
            env.BUILD_TIME = new Date().format("yyyyMMdd-HHmmss")
            env.BUILD_TAG = PROJECT_VERSION + "-" + BUILD_TIME
          }

        }

      }
    }

    stage('代码分析') {
      agent none
      steps {
        container('maven') {
          withCredentials([string(credentialsId : 'lucumt-sonar-token' ,variable : 'SONAR_TOKEN' ,)]) {
            withSonarQubeEnv('sonar') {
              sh '''echo $PROJECT_VERSION
mvn sonar:sonar \\
  -Dsonar.projectKey=lucumt-system \\
  -Dsonar.host.url=http://10.30.5.170:32387 \\
  -Dsonar.login=$SONAR_TOKEN'''
            }

          }

          timeout(unit: 'HOURS', activity: true, time: 1) {
            waitForQualityGate 'false'
          }

        }

      }
    }

    stage('项目编译') {
      agent none
      steps {
        container('maven') {
          sh 'ls'
          sh 'mvn clean compile package -Dmaven.test.skip=true'
        }

      }
    }

    stage('制品保存') {
      agent none
      steps {
        container('maven') {
          archiveArtifacts 'app/target/*.jar'
        }

      }
    }

    stage('镜像构建') {
      agent none
      steps {
        container('maven') {
          sh '''docker build -f kubesphere/Dockerfile \\
-t lucumt-system:$BUILD_TAG  \\
--build-arg  PROJECT_VERSION=$PROJECT_VERSION \\
--build-arg  NODE_PORT=$NODE_PORT \\
--build-arg PRODUCT_PHASE=$PRODUCT_PHASE .'''
        }

      }
    }

    stage('镜像推送') {
      agent none
      steps {
        container('maven') {
          withCredentials([usernamePassword(credentialsId : 'harbor-account' ,usernameVariable : 'DOCKER_USER_VAR' ,passwordVariable : 'DOCKER_PWD_VAR' ,)]) {
            sh 'echo "$DOCKER_PWD_VAR" | docker login $REGISTRY -u "$DOCKER_USER_VAR" --password-stdin'
            sh '''docker tag  lucumt-system:$BUILD_TAG $REGISTRY/$DOCKERHUB_NAMESPACE/lucumt-system:$BUILD_TAG
docker push  $REGISTRY/$DOCKERHUB_NAMESPACE/lucumt-system:$BUILD_TAG'''
          }

        }

      }
    }

    stage('部署到dev') {
      agent none
      steps {
        kubernetesDeploy(enableConfigSubstitution: true, deleteResource: false, kubeconfigId: 'lucumt-kubeconfig', configs: 'kubesphere/deploy.yml')
      }
    }

  }
  environment {
    DOCKER_CREDENTIAL_ID = 'harbor-id'
    GITHUB_CREDENTIAL_ID = 'gitlab-id'
    KUBECONFIG_CREDENTIAL_ID = 'lucumt-kubeconfig'
    REGISTRY = '10.30.5.170:30005'
    DOCKERHUB_NAMESPACE = 'lucumt-library'
    GITHUB_ACCOUNT = 'kubesphere'
  }
}